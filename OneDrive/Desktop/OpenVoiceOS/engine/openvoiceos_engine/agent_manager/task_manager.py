import asyncio
import base64
import copy
import json
import math
import os
import random
import time
import traceback
import uuid

import aiohttp
import pytz
from semantic_router import Route
from semantic_router.encoders import FastEmbedEncoder
from semantic_router.layer import RouteLayer

from openvoiceos_engine.agent_types import (ExtractionContextualAgent, GraphAgent,
                                          RAGAgent,
                                          StreamingContextualAgent,
                                          SummarizationContextualAgent,
                                          WebhookAgent)
from openvoiceos_engine.constants import (ACCIDENTAL_INTERRUPTION_PHRASES,
                                          CHECK_FOR_COMPLETION_PROMPT,
                                          DEFAULT_LANGUAGE_CODE,
                                          DEFAULT_TIMEZONE,
                                          DEFAULT_USER_ONLINE_MESSAGE,
                                          DEFAULT_USER_ONLINE_MESSAGE_TRIGGER_DURATION,
                                          FILLER_DICT, FILLER_PROMPT,
                                          DATE_PROMPT)
from openvoiceos_engine.helpers.function_calling_helpers import (
    computed_api_response, trigger_api)
from openvoiceos_engine.helpers.logger_config import configure_logger
from openvoiceos_engine.helpers.mark_event_meta_data import MarkEventMetaData
from openvoiceos_engine.helpers.observable_variable import ObservableVariable
from openvoiceos_engine.helpers.utils import (
    calculate_audio_duration, clean_json_string,
    compute_function_pre_call_message, convert_to_request_log,
    create_ws_data_packet, format_messages, get_date_time_from_timezone,
    get_file_names_in_directory, get_md5_hash, get_prompt_responses,
    get_raw_audio_bytes, get_required_input_types, get_route_info,
    is_valid_md5, process_task_cancellation, resample,
    save_audio_file_to_s3, update_prompt_with_context, wav_bytes_to_pcm,
    yield_chunks_from_memory)
from openvoiceos_engine.memory.cache.vector_cache import VectorCache
from openvoiceos_engine.prompts import EXTRACTION_PROMPT, SUMMARIZATION_PROMPT
from openvoiceos_engine.providers import (SUPPORTED_INPUT_HANDLERS,
                                          SUPPORTED_INPUT_TELEPHONY_HANDLERS,
                                          SUPPORTED_LLM_PROVIDERS,
                                          SUPPORTED_OUTPUT_HANDLERS,
                                          SUPPORTED_OUTPUT_TELEPHONY_HANDLERS,
                                          SUPPORTED_SYNTHESIZER_MODELS,
                                          SUPPORTED_TRANSCRIBER_MODELS,
                                          SUPPORTED_TRANSCRIBER_PROVIDERS)

from .base_manager import BaseManager

asyncio.get_event_loop().set_debug(True)
logger = configure_logger(__name__)


class TaskManager(BaseManager):
    def __init__(self, assistant_name, task_id, task, ws, input_parameters=None, context_data=None,
                 assistant_id=None, turn_based_conversation=False, cache=None,
                 input_queue=None, conversation_history=None, output_queue=None, yield_chunks=True, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.kwargs["task_manager_instance"] = self
        self.llm_latencies = {'connection_latency_ms': None, 'turn_latencies': []}
        self.transcriber_latencies = {'connection_latency_ms': None, 'turn_latencies': []}
        self.synthesizer_latencies = {'connection_latency_ms': None, 'turn_latencies': []}

        self.task_config = task

        self.timezone = pytz.timezone(DEFAULT_TIMEZONE)
        self.language = DEFAULT_LANGUAGE_CODE

        if task.get('tools_config', {}).get('api_tools'):
            self.kwargs['api_tools'] = task['tools_config']['api_tools']

        if task.get('tools_config', {}).get("llm_agent", {}).get('llm_config', {}).get('assistant_id'):
            self.kwargs['assistant_id'] = task['tools_config']["llm_agent"]['llm_config']['assistant_id']

        logger.info(f"doing task {task}")
        self.task_id = task_id
        self.assistant_name = assistant_name
        self.tools = {}
        self.websocket = ws
        self.context_data = context_data
        self.turn_based_conversation = turn_based_conversation
        self.enforce_streaming = kwargs.get("enforce_streaming", False)
        self.room_url = kwargs.get("room_url", None)
        self.is_web_based_call = kwargs.get("is_web_based_call", False)
        self.yield_chunks = False

        self.audio_queue = asyncio.Queue()
        self.llm_queue = asyncio.Queue()
        self.synthesizer_queue = asyncio.Queue()
        self.transcriber_output_queue = asyncio.Queue()
        self.queues = {
            "transcriber": self.audio_queue,
            "llm": self.llm_queue,
            "synthesizer": self.synthesizer_queue
        }
        self.pipelines = task.get('toolchain', {}).get('pipelines', [])
        self.textual_chat_agent = False
        if self.pipelines and self.pipelines[0] == "llm" and task.get("tools_config", {}).get("llm_agent", {}).get("agent_task") == "conversation":
            self.textual_chat_agent = False

        self.assistant_id = assistant_id
        self.run_id = kwargs.get("run_id")

        self.mark_event_meta_data = MarkEventMetaData()
        self.sampling_rate = 24000
        self.conversation_ended = False
        self.hangup_triggered = False

        self.prompts, self.system_prompt = {}, {}
        self.input_parameters = input_parameters

        self.should_record = False
        self.conversation_recording = {
            "input": {'data': b'', 'started': time.time()},
            "output": [],
            "metadata": {"started": 0}
        }

        self.welcome_message_audio = self.kwargs.pop('welcome_message_audio', None)
        self.observable_variables = {}

        if task_id == 0:
            if self.is_web_based_call:
                self.task_config["tools_config"]["input"]["provider"] = "default"
                self.task_config["tools_config"]["output"]["provider"] = "default"

            self.default_io = self.task_config["tools_config"]["output"]["provider"] == 'default'
            self.observable_variables["agent_hangup_observable"] = ObservableVariable(False)
            self.observable_variables["agent_hangup_observable"].add_observer(self.agent_hangup_observer)

            self.observable_variables["final_chunk_played_observable"] = ObservableVariable(False)
            self.observable_variables["final_chunk_played_observable"].add_observer(self.final_chunk_played_observer)

            if self.is_web_based_call:
                self.observable_variables["init_event_observable"] = ObservableVariable(None)
                self.observable_variables["init_event_observable"].add_observer(self.handle_init_event)

            self.should_record = self.task_config["tools_config"]["output"]["provider"] == 'default' and self.enforce_streaming
            self.__setup_input_handlers(turn_based_conversation, input_queue, self.should_record)

        self.__setup_output_handlers(turn_based_conversation, output_queue)

        self.history = [] if conversation_history is None else conversation_history
        self.interim_history = copy.deepcopy(self.history.copy())
        self.label_flow = []

        self.llm_task = None
        self.execute_function_call_task = None
        self.synthesizer_tasks = []
        self.synthesizer_task = None
        self.synthesizer_monitor_task = None

        self.current_request_id = None
        self.previous_request_id = None
        self.llm_rejected_request_ids = set()
        self.llm_processed_request_ids = set()
        self.buffers = []
        self.should_respond = False
        self.last_response_time = time.time()
        self.consider_next_transcript_after = time.time()
        self.callee_speaking = False
        self.callee_speaking_start_time = -1
        self.llm_response_generated = False
        self.turn_id = 0

        self.call_sid = None
        self.stream_sid = None

        self.transcriber_duration = 0
        self.synthesizer_characters = 0
        self.ended_by_assistant = False
        self.start_time = time.time()

        self.extracted_data = None
        self.summarized_data = None
        self.stream = (self.task_config.get("tools_config", {}).get('synthesizer') is not None and self.task_config["tools_config"]["synthesizer"]["stream"]) and (self.enforce_streaming or not self.turn_based_conversation)

        self.is_local = False
        self.llm_config = None
        self.agent_type = None
        self.llm_agent_config = {}

        self.llm_config_map = {}
        self.llm_agent_map = {}
        if self.__is_multiagent():
            for agent, config in self.task_config["tools_config"]["llm_agent"]['llm_config']['agent_map'].items():
                self.llm_config_map[agent] = config.copy()
                self.llm_config_map[agent]['buffer_size'] = self.task_config["tools_config"]["synthesizer"]['buffer_size']
        else:
            if self.task_config.get("tools_config", {}).get("llm_agent") is not None:
                self.llm_agent_config = self.task_config["tools_config"]["llm_agent"]
                self.llm_config = self.llm_agent_config.get('llm_config', self.llm_agent_config)

        self.output_task = None
        self.buffered_output_queue = asyncio.Queue()

        self.cache = cache
        logger.info("task initialization completed")

        self.curr_sequence_id = 0
        self.sequence_ids = {-1}

        self.request_logs = []
        self.hangup_task = None
        self.conversation_config = None

        if task_id == 0:
            provider_config = self.task_config.get("tools_config", {}).get("synthesizer", {}).get("provider_config", {})
            self.synthesizer_voice = provider_config.get("voice", "default_voice")

            self.handle_accumulated_message_task = None
            self.hangup_task = None
            self.transcriber_task = None
            self.output_chunk_size = 16384 if self.sampling_rate == 24000 else 4096
            self.nitro = True
            self.conversation_config = task.get("task_config", {})
            logger.info(f"Conversation config {self.conversation_config}")
            self.generate_precise_transcript = self.conversation_config.get('generate_precise_transcript', False)

            self.trigger_user_online_message_after = self.conversation_config.get("trigger_user_online_message_after", DEFAULT_USER_ONLINE_MESSAGE_TRIGGER_DURATION)
            self.check_if_user_online = self.conversation_config.get("check_if_user_online", True)
            self.check_user_online_message = self.conversation_config.get("check_user_online_message", DEFAULT_USER_ONLINE_MESSAGE)

            self.kwargs["process_interim_results"] = "true" if self.conversation_config.get("optimize_latency", False) is True else "false"
            logger.info(f"Processing interim results {self.kwargs['process_interim_results'] }")

            self.routes = task.get('tools_config', {}).get('llm_agent', {}).get("routes")
            self.route_layer = None

            if self.routes:
                start_time = time.time()
                routes_meta = self.kwargs.get('routes')
                if routes_meta:
                    self.vector_caches = routes_meta.get("vector_caches", {})
                    self.route_responses_dict = routes_meta.get("route_responses_dict", {})
                    self.route_layer = routes_meta.get("route_layer")
                    logger.info(f"Time to setup routes from warmed up cache {time.time() - start_time}")
                else:
                    self.__setup_routes(self.routes)
                    logger.info(f"Time to setup routes {time.time() - start_time}")

            if self.__is_multiagent():
                routes_meta = self.kwargs.pop('routes', {})
                self.agent_routing = routes_meta.get('agent_routing_config', {}).get('route_layer')
                self.default_agent = task['tools_config']['llm_agent']['llm_config']['default_agent']
                logger.info(f"Initialised with default agent {self.default_agent}, agent_routing {self.agent_routing}")

            if self.conversation_config is not None:
                self.minimum_wait_duration = self.task_config["tools_config"]["transcriber"]["endpointing"]
                self.last_spoken_timestamp = time.time() * 1000
                self.incremental_delay = self.conversation_config.get("incremental_delay", 100)
                self.required_delay_before_speaking = max(self.minimum_wait_duration - self.incremental_delay, 0)
                self.time_since_first_interim_result = -1

                self.hang_conversation_after = self.conversation_config.get("hangup_after_silence", 10)
                self.last_transmitted_timestamp = 0
                self.let_remaining_audio_pass_through = False

                self.use_llm_to_determine_hangup = self.conversation_config.get("hangup_after_LLMCall", False)
                self.check_for_completion_prompt = None
                if self.use_llm_to_determine_hangup:
                    self.check_for_completion_prompt = self.conversation_config.get("call_cancellation_prompt", CHECK_FOR_COMPLETION_PROMPT)
                    self.check_for_completion_prompt += """\nRespond only in this JSON format: {"hangup": "Yes" or "No"}"""

                self.call_hangup_message = self.conversation_config.get("call_hangup_message", None)
                if self.call_hangup_message and self.context_data and not self.is_web_based_call:
                    self.call_hangup_message = update_prompt_with_context(self.call_hangup_message, self.context_data)
                
                self.check_for_completion_llm = os.getenv("CHECK_FOR_COMPLETION_LLM")
                self.time_since_last_spoken_human_word = 0

                self.number_of_words_for_interruption = self.conversation_config.get("number_of_words_for_interruption", 3)
                self.asked_if_user_is_still_there = False
                self.started_transmitting_audio = False
                self.accidental_interruption_phrases = set(ACCIDENTAL_INTERRUPTION_PHRASES)
                self.allow_extra_sleep = False

                self.should_backchannel = self.conversation_config.get("backchanneling", False)
                self.backchanneling_task = None
                self.backchanneling_start_delay = self.conversation_config.get("backchanneling_start_delay", 5)
                self.backchanneling_message_gap = self.conversation_config.get("backchanneling_message_gap", 2)
                if self.should_backchannel and not turn_based_conversation and task_id == 0:
                    backchanneling_audio_location = kwargs.get("backchanneling_audio_location", os.getenv("BACKCHANNELING_PRESETS_DIR"))
                    self.backchanneling_audios = f'{backchanneling_audio_location}/{self.synthesizer_voice.lower()}'
                    try:
                        self.filenames = get_file_names_in_directory(self.backchanneling_audios)
                    except Exception as e:
                        logger.error(f"Could not load backchanneling audios, disabling feature: {e}")
                        self.should_backchannel = False
                
                if "agent_welcome_message" in self.kwargs:
                    self.first_message_task = None
                    self.transcriber_message = ''

                self.ambient_noise = self.conversation_config.get("ambient_noise", False)
                self.ambient_noise_task = None
                if self.ambient_noise:
                    self.soundtrack = f"{self.conversation_config.get('ambient_noise_track', 'coffee-shop')}.wav"
            
            self.use_fillers = self.conversation_config.get("use_fillers", False)
            if self.use_fillers:
                self.filler_classifier = kwargs.get("classifier")
                if self.filler_classifier:
                    self.filler_preset_directory = f"{os.getenv('FILLERS_PRESETS_DIR')}/{self.synthesizer_voice.lower()}"

        self.__setup_transcriber()
        self.__setup_synthesizer(self.llm_config)
        self.__setup_llm_and_agent(task_id)

    def __setup_llm_and_agent(self, task_id):
        if self.llm_config is not None:
            llm = self.__setup_llm(self.llm_config, task_id)
            agent_params = {
                'llm': llm,
                'agent_type': self.llm_agent_config.get("agent_type", "simple_llm_agent")
            }
            self.__setup_tasks(**agent_params)
        elif self.__is_multiagent():
            for agent in self.task_config["tools_config"]["llm_agent"]['llm_config']['agent_map']:
                llm_config = self.llm_config_map.get(agent, {})
                if 'routes' in llm_config:
                    del llm_config['routes']
                llm = self.__setup_llm(llm_config)
                agent_type = llm_config.get("agent_type", "simple_llm_agent")
                agent_params = {'llm': llm, 'agent_type': agent_type}
                llm_agent = self.__setup_tasks(**agent_params)
                self.llm_agent_map[agent] = llm_agent
        elif self.task_config["task_type"] == "webhook":
            webhook_url = self.task_config["tools_config"]["api_tools"].get("webhookURL") or self.task_config["tools_config"]["api_tools"]["tools_params"]["webhook"]["url"]
            self.tools["webhook_agent"] = WebhookAgent(webhook_url=webhook_url)

    def __is_multiagent(self):
        if self.task_config.get("task_type") == "webhook":
            return False
        return self.task_config.get('tools_config', {}).get("llm_agent", {}).get("agent_type") == "multiagent"
    
    def __is_knowledgebase_agent(self):
        if self.task_config.get("task_type") == "webhook":
            return False
        return self.task_config.get('tools_config', {}).get("llm_agent", {}).get("agent_type") == "knowledgebase_agent"

    def __is_graph_agent(self):
        if self.task_config.get("task_type") == "webhook":
            return False
        return self.task_config.get('tools_config', {}).get("llm_agent", {}).get("agent_type") == "graph_agent"

    def __setup_routes(self, routes_config):
        embedding_model = routes_config.get("embedding_model", os.getenv("ROUTE_EMBEDDING_MODEL"))
        route_encoder = FastEmbedEncoder(name=embedding_model)

        routes_list = []
        self.vector_caches = {}
        self.route_responses_dict = {}

        for route in routes_config.get('routes', []):
            utterances = route['utterances']
            r = Route(name=route['route_name'], utterances=utterances, score_threshold=route.get('score_threshold', 0.85))
            
            if isinstance(route['response'], list) and len(route['response']) == len(utterances):
                self.route_responses_dict[route['route_name']] = dict(zip(utterances, route['response']))
                vector_cache = VectorCache(embedding_model=embedding_model)
                vector_cache.set(utterances)
                self.vector_caches[route['route_name']] = vector_cache
            elif isinstance(route['response'], str):
                self.route_responses_dict[route['route_name']] = route['response']
            else:
                logger.error("Invalid response format for route. It must be a string or a list of strings matching utterances.")

            routes_list.append(r)
            
        self.route_layer = RouteLayer(encoder=route_encoder, routes=routes_list)
        logger.info("Routes setup is complete.")

    def __setup_output_handlers(self, turn_based_conversation, output_queue):
        output_provider = self.task_config.get("tools_config", {}).get("output", {}).get("provider")
        if not output_provider:
            logger.info("No output handler configured.")
            return

        output_kwargs = {"websocket": self.websocket}
        if output_provider in SUPPORTED_OUTPUT_HANDLERS:
            handler_class = SUPPORTED_OUTPUT_HANDLERS.get("default") if turn_based_conversation else SUPPORTED_OUTPUT_HANDLERS.get(output_provider)
            
            if output_provider == "daily":
                output_kwargs['room_url'] = self.room_url
            elif output_provider in SUPPORTED_OUTPUT_TELEPHONY_HANDLERS:
                output_kwargs['mark_event_meta_data'] = self.mark_event_meta_data
                self.task_config['tools_config']['synthesizer']['provider_config']['sampling_rate'] = 8000
                self.task_config['tools_config']['synthesizer']['audio_format'] = 'pcm'
            else:
                self.task_config['tools_config']['synthesizer']['provider_config']['sampling_rate'] = 24000
                output_kwargs['queue'] = output_queue
            
            self.sampling_rate = self.task_config.get('tools_config', {}).get('synthesizer', {}).get('provider_config', {}).get('sampling_rate', 24000)
            if output_provider == "default":
                output_kwargs["is_web_based_call"] = self.is_web_based_call
                output_kwargs['mark_event_meta_data'] = self.mark_event_meta_data

            self.tools["output"] = handler_class(**output_kwargs)
        else:
            logger.error(f"Unsupported output handler: {output_provider}")

    def __setup_input_handlers(self, turn_based_conversation, input_queue, should_record):
        input_provider = self.task_config.get("tools_config", {}).get("input", {}).get("provider")
        if not input_provider:
            logger.info("No input handler configured.")
            return
            
        if input_provider in SUPPORTED_INPUT_HANDLERS:
            input_kwargs = {
                "queues": self.queues,
                "websocket": self.websocket,
                "input_types": get_required_input_types(self.task_config),
                "mark_event_meta_data": self.mark_event_meta_data,
                "is_welcome_message_played": self.task_config.get("tools_config", {}).get("output", {}).get("provider") == 'default' and not self.is_web_based_call
            }

            if input_provider == "daily":
                input_kwargs['room_url'] = self.room_url

            if should_record:
                input_kwargs['conversation_recording'] = self.conversation_recording

            if turn_based_conversation:
                input_kwargs['turn_based_conversation'] = True
                handler_class = SUPPORTED_INPUT_HANDLERS.get("default")
                input_kwargs['queue'] = input_queue
            else:
                handler_class = SUPPORTED_INPUT_HANDLERS.get(input_provider)
                if input_provider == 'default':
                    input_kwargs['queue'] = input_queue
                input_kwargs["observable_variables"] = self.observable_variables

            self.tools["input"] = handler_class(**input_kwargs)
        else:
            logger.error(f"Unsupported input handler: {input_provider}")

    def __setup_transcriber(self):
        transcriber_config = self.task_config.get("tools_config", {}).get("transcriber")
        if not transcriber_config:
            return
            
        try:
            self.language = transcriber_config.get('language', DEFAULT_LANGUAGE_CODE)
            provider_type = "web_based_call" if self.is_web_based_call else self.task_config["tools_config"]["input"]["provider"]

            transcriber_config.update({
                "input_queue": self.audio_queue,
                "output_queue": self.transcriber_output_queue
            })

            transcriber_provider = transcriber_config.get("provider", "deepgram")
            transcriber_class = SUPPORTED_TRANSCRIBER_PROVIDERS.get(transcriber_provider)
            if transcriber_class:
                self.tools["transcriber"] = transcriber_class(provider_type, **transcriber_config, **self.kwargs)
            else:
                logger.error(f"Unsupported transcriber provider: {transcriber_provider}")
        except Exception as e:
            logger.error(f"Error setting up transcriber: {e}", exc_info=True)

    def __setup_synthesizer(self, llm_config=None):
        synthesizer_config = self.task_config.get("tools_config", {}).get("synthesizer")
        if not synthesizer_config:
            return
            
        if self._is_conversation_task():
            self.kwargs["use_turbo"] = synthesizer_config.get('language') == DEFAULT_LANGUAGE_CODE
        
        caching = synthesizer_config.pop("caching", True)
        self.synthesizer_provider = synthesizer_config.pop("provider")
        synthesizer_class = SUPPORTED_SYNTHESIZER_MODELS.get(self.synthesizer_provider)
        
        if synthesizer_class:
            provider_config = synthesizer_config.pop("provider_config")
            self.synthesizer_voice = provider_config.get("voice")
            if self.turn_based_conversation:
                synthesizer_config["audio_format"] = "mp3"
                synthesizer_config["stream"] = self.enforce_streaming
            
            self.tools["synthesizer"] = synthesizer_class(**synthesizer_config, **provider_config, **self.kwargs, caching=caching)
            
            if not self.turn_based_conversation:
                self.synthesizer_monitor_task = asyncio.create_task(self.tools['synthesizer'].monitor_connection())
            
            if llm_config:
                llm_config["buffer_size"] = synthesizer_config.get('buffer_size')
        else:
            logger.error(f"Unsupported synthesizer provider: {self.synthesizer_provider}")

    def __setup_llm(self, llm_config, task_id=0):
        if not llm_config:
            return None
        
        provider = llm_config.get("provider")
        llm_class = SUPPORTED_LLM_PROVIDERS.get(provider)
        
        if llm_class:
            current_kwargs = self.kwargs.copy()
            if task_id > 0:
                current_kwargs.pop('llm_key', None)
                current_kwargs.pop('base_url', None)
                current_kwargs.pop('api_version', None)
                if self._is_summarization_task() or self._is_extraction_task():
                    llm_config['model'] = 'gpt-4o-mini'
            
            return llm_class(language=self.language, **llm_config, **current_kwargs)
        else:
            logger.error(f"Unsupported LLM provider: {provider}")
            return None

    def __get_agent_object(self, llm, agent_type, assistant_config=None):
        self.agent_type = agent_type
        agent_classes = {
            "simple_llm_agent": StreamingContextualAgent,
            "knowledgebase_agent": RAGAgent,
            "graph_agent": GraphAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"{agent_type} Agent type is not supported.")
            
        if agent_type == "knowledgebase_agent":
            llm_config = self.llm_agent_config.get("llm_config", {})
            vector_store_config = llm_config.get("vector_store", {})
            return RAGAgent(
                provider_config=vector_store_config,
                temperature=llm_config.get("temperature", 0.1),
                model=llm_config.get("model", "gpt-3.5-turbo-16k"),
                buffer=self.task_config["tools_config"]["synthesizer"].get('buffer_size'),
                max_tokens=self.llm_agent_config.get('max_tokens', 100)
            )
        elif agent_type == "graph_agent":
            llm_config = self.llm_agent_config.get("llm_config", {})
            return GraphAgent(llm_config)
        else: 
            return StreamingContextualAgent(llm)

    def __setup_tasks(self, llm=None, agent_type=None, assistant_config=None):
        task_type = self.task_config.get("task_type")
        
        if task_type == "conversation":
            if self.__is_multiagent():
                return self.__get_agent_object(llm, agent_type, assistant_config)
            else:
                self.tools["llm_agent"] = self.__get_agent_object(llm, agent_type, assistant_config)
        elif task_type == "extraction":
            self.tools["llm_agent"] = ExtractionContextualAgent(llm, prompt=self.system_prompt)
            self.extracted_data = None
        elif task_type == "summarization":
            self.tools["llm_agent"] = SummarizationContextualAgent(llm, prompt=self.system_prompt)
            self.summarized_data = None
            
        logger.info("Agent and task setup completed.")
    
    def __get_final_prompt(self, prompt, today, current_time, current_timezone):
        enriched_prompt = prompt
        if self.context_data is not None:
            enriched_prompt = update_prompt_with_context(enriched_prompt, self.context_data)
        notes = "### Note:\n"
        if self._is_conversation_task() and self.use_fillers:
            notes += f"1.{FILLER_PROMPT}\n"
        return f"{enriched_prompt}\n{notes}\n{DATE_PROMPT.format(today, current_time, current_timezone)}"

    async def load_prompt(self, assistant_name, task_id, local, **kwargs):
        if self.task_config["task_type"] == "webhook":
            return

        agent_type = self.llm_agent_config.get("agent_type", "simple_llm_agent")
        if agent_type in ["knowledgebase_agent"]:
            return

        self.is_local = local
        if task_id == 0:
            recipient_data = self.context_data.get('recipient_data', {}) if self.context_data else {}
            if recipient_data and recipient_data.get('timezone'):
                self.timezone = pytz.timezone(recipient_data['timezone'])

        current_date, current_time = get_date_time_from_timezone(self.timezone)

        prompt_responses = kwargs.get('prompt_responses')
        if not prompt_responses:
            prompt_responses = await get_prompt_responses(assistant_id=self.assistant_id, local=self.is_local)

        current_task = f"task_{task_id + 1}"
        if self.__is_multiagent():
            prompts = prompt_responses.get(current_task, {})
            self.prompt_map = {}
            for agent in self.task_config["tools_config"]["llm_agent"]['llm_config']['agent_map']:
                prompt = prompts.get(agent, {}).get('system_prompt', '')
                prompt = self.__prefill_prompts(self.task_config, prompt, self.task_config['task_type'])
                prompt = self.__get_final_prompt(prompt, current_date, current_time, self.timezone)
                if agent == self.task_config["tools_config"]["llm_agent"]['llm_config']['default_agent']:
                    self.system_prompt = {'role': 'system', 'content': prompt}
                self.prompt_map[agent] = prompt
        else:
            self.prompts = self.__prefill_prompts(self.task_config, prompt_responses.get(current_task), self.task_config['task_type'])

        if "system_prompt" in self.prompts:
            enriched_prompt = self.prompts["system_prompt"]
            if self.context_data and not self.is_web_based_call:
                enriched_prompt = update_prompt_with_context(enriched_prompt, self.context_data)
                if self.context_data.get('recipient_data', {}).get('call_sid'):
                    self.call_sid = self.context_data['recipient_data']['call_sid']
                    enriched_prompt += f'\nPhone call_sid is "{self.call_sid}"'
                enriched_prompt += f'\nagent_id is "{self.assistant_id}"\nexecution_id is "{self.run_id}"'
                self.prompts["system_prompt"] = enriched_prompt

            notes = "### Note:\n"
            if self._is_conversation_task() and self.use_fillers:
                notes += f"1.{FILLER_PROMPT}\n"
            
            self.system_prompt = {
                'role': "system",
                'content': f"{enriched_prompt}\n{notes}\n{DATE_PROMPT.format(current_date, current_time, self.timezone)}"
            }
        else:
            self.system_prompt = {'role': "system", 'content': ""}

        if self.system_prompt['content']:
            self.history = [self.system_prompt] + self.history if self.history else [self.system_prompt]
        
        if task_id == 0 and len(self.history) <= 1 and self.kwargs.get('agent_welcome_message'):
            self.history.append({'role': 'assistant', 'content': self.kwargs['agent_welcome_message']})

        self.interim_history = copy.deepcopy(self.history)

    def __prefill_prompts(self, task, prompt, task_type):
        if self.context_data and self.context_data.get('recipient_data', {}).get('timezone'):
            self.timezone = pytz.timezone(self.context_data['recipient_data']['timezone'])
        
        current_date, current_time = get_date_time_from_timezone(self.timezone)

        if not prompt and task_type in ('extraction', 'summarization'):
            if task_type == 'extraction':
                extraction_json = task.get("tools_config", {}).get('llm_agent', {}).get('llm_config', {}).get('extraction_json')
                return {"system_prompt": EXTRACTION_PROMPT.format(current_date, current_time, self.timezone, extraction_json)}
            elif task_type == 'summarization':
                return {"system_prompt": SUMMARIZATION_PROMPT}
        return prompt if prompt else {}

    # ... (rest of the file's methods will be added in subsequent responses)

        # ... (Continuing from the __init__ and setup methods from the previous response)

    def _is_extraction_task(self):
        return self.task_config["task_type"] == "extraction"

    def _is_summarization_task(self):
        return self.task_config["task_type"] == "summarization"

    def _is_conversation_task(self):
        return self.task_config["task_type"] == "conversation"

    def _get_next_step(self, sequence, origin):
        try:
            return next((self.pipelines[sequence][i + 1] for i in range(len(self.pipelines[sequence]) - 1) if
                         self.pipelines[sequence][i] == origin), "output")
        except Exception as e:
            logger.error(f"Error getting next step: {e}")
            return "output"

    def __process_stop_words(self, text_chunk, meta_info):
        if "end_of_llm_stream" in meta_info and meta_info["end_of_llm_stream"] and "user" in text_chunk[-5:].lower():
            if text_chunk[-5:].lower() == "user:":
                text_chunk = text_chunk[:-5]
            elif text_chunk[-4:].lower() == "user":
                text_chunk = text_chunk[:-4]
        return text_chunk

    async def _handle_llm_output(self, next_step, text_chunk, should_bypass_synth, meta_info, is_filler=False):
        logger.info(f"Received text from LLM for output processing: {text_chunk} (seq_id: {meta_info['sequence_id']})")
        if "request_id" not in meta_info:
            meta_info["request_id"] = str(uuid.uuid4())

        if not self.stream and not is_filler:
            meta_info["llm_first_buffer_generation_latency"] = time.time() - meta_info["llm_start_time"]
        elif is_filler:
            meta_info.update({'origin': "classifier", 'cached': True, 'local': True, 'message_category': 'filler'})

        if next_step == "synthesizer" and not should_bypass_synth:
            task = asyncio.create_task(self._synthesize(create_ws_data_packet(text_chunk, meta_info)))
            self.synthesizer_tasks.append(asyncio.ensure_future(task))
        elif self.tools.get("output"):
            await self.tools["output"].handle(create_ws_data_packet(text_chunk, meta_info))

    def _set_call_details(self, message):
        if "call_sid" in message.get('meta_info', {}):
            self.call_sid = message['meta_info']["call_sid"]
        if "stream_sid" in message.get('meta_info', {}):
            self.stream_sid = message['meta_info']["stream_sid"]

    async def _process_followup_task(self, message=None):
        if self.task_config["task_type"] == "webhook":
            extraction_details = self.input_parameters.get('extraction_details', {})
            self.webhook_response = await self.tools["webhook_agent"].execute(extraction_details)
        else:
            message_content = format_messages(self.input_parameters["messages"], include_tools=True)
            self.history.append({'role': 'user', 'content': message_content})
            json_data = await self.tools["llm_agent"].generate(self.history)
            
            if self.task_config["task_type"] == "summarization":
                self.summarized_data = json_data.get("summary", "")
            else:
                cleaned_data = clean_json_string(json_data)
                self.extracted_data = json.loads(cleaned_data) if isinstance(cleaned_data, str) else cleaned_data

    async def __cleanup_downstream_tasks(self):
        current_ts = time.time()
        logger.info("Cleaning up downstream tasks")
        
        await self.tools["synthesizer"].handle_interruption()
        await self.tools["output"].handle_interruption()
        self.sequence_ids = {-1}
        
        if self.output_task:
            self.output_task.cancel()
            self.output_task = None
        if self.llm_task:
            self.llm_task.cancel()
            self.llm_task = None
        if self.first_message_task:
            self.first_message_task.cancel()
            self.first_message_task = None

        if not self.buffered_output_queue.empty():
            self.buffered_output_queue = asyncio.Queue()

        self.output_task = asyncio.create_task(self.__process_output_loop())
        self.started_transmitting_audio = False
        self.last_transmitted_timestamp = time.time()

    def __get_updated_meta_info(self, meta_info=None):
        meta_info_copy = (meta_info or self.tools["transcriber"].get_meta_info()).copy()
        self.curr_sequence_id += 1
        meta_info_copy["sequence_id"] = self.curr_sequence_id
        meta_info_copy['turn_id'] = self.turn_id
        self.sequence_ids.add(self.curr_sequence_id)
        return meta_info_copy

    async def _run_llm_task(self, message):
        sequence, meta_info = self._extract_sequence_and_meta(message)
        try:
            if self._is_extraction_task() or self._is_summarization_task():
                await self._process_followup_task(message)
            elif self._is_conversation_task():
                await self._process_conversation_task(message, sequence, meta_info)
            else:
                logger.error(f"Unsupported task type: {self.task_config['task_type']}")
            self.llm_task = None
        except Exception as e:
            logger.error(f"Error in LLM task: {e}", exc_info=True)

    def _extract_sequence_and_meta(self, message):
        sequence, meta_info = None, None
        if isinstance(message, dict) and "meta_info" in message:
            self._set_call_details(message)
            sequence = message["meta_info"].get("sequence")
            meta_info = message["meta_info"]
        return sequence, meta_info
    
    async def final_chunk_played_observer(self, is_final_chunk_played):
        self.last_transmitted_timestamp = time.time()

    async def agent_hangup_observer(self, is_agent_hangup):
        if is_agent_hangup:
            self.tools["output"].set_hangup_sent()
            await self.__process_end_of_conversation()

    async def wait_for_current_message(self):
        while not self.conversation_ended:
            mark_events = self.mark_event_meta_data.mark_event_meta_data
            if not mark_events:
                break
            
            first_item = list(mark_events.values())[0]
            if first_item.get('is_final_chunk'):
                break
            
            await asyncio.sleep(0.1)

    async def __process_end_of_conversation(self, web_call_timeout=False):
        logger.info("Processing end of conversation.")
        await self.wait_for_current_message()

        if self.call_hangup_message and not web_call_timeout:
            self.history.append({"role": "assistant", "content": self.call_hangup_message})

        self.conversation_ended = True
        self.ended_by_assistant = True
        await self.tools["input"].stop_handler()
        if "transcriber" in self.tools and not self.turn_based_conversation:
            await self.tools["transcriber"].toggle_connection()

    async def _process_conversation_task(self, message, sequence, meta_info):
        should_bypass_synth = 'bypass_synth' in meta_info and meta_info['bypass_synth']
        next_step = self._get_next_step(sequence, "llm")
        meta_info['llm_start_time'] = time.time()
        
        route = None
        if self.__is_multiagent() and self.agent_routing:
            route_info = await asyncio.to_thread(lambda: get_route_info(message['data'], self.agent_routing))
            self.tools['llm_agent'] = self.llm_agent_map.get(route_info, self.llm_agent_map[self.default_agent])
        
        if self.route_layer:
            route_info = await asyncio.to_thread(lambda: self.route_layer(message['data']))
            if route_info:
                route = route_info.name

        if route:
            logger.info(f"Route hit: {route}. Responding from cache.")
            if route in self.vector_caches:
                relevant_utterance = self.vector_caches[route].get(message['data'])
                cache_response = self.route_responses_dict[route][relevant_utterance]
            else:
                cache_response = self.route_responses_dict[route]
            
            meta_info.update({'cached': True, "end_of_llm_stream": True})
            await self._handle_llm_output(next_step, cache_response, should_bypass_synth, meta_info)
        else:
            messages = copy.deepcopy(self.history)
            messages.append({'role': 'user', 'content': message['data']})
            await self.__do_llm_generation(messages, meta_info, next_step, should_bypass_synth)

    async def __do_llm_generation(self, messages, meta_info, next_step, should_bypass_synth=False, should_trigger_function_call=False):
        llm_response = ""
        synthesize = not should_bypass_synth
        
        async for llm_message in self.tools['llm_agent'].generate(messages, synthesize=synthesize, meta_info=meta_info):
            data, end_of_llm_stream, latency, trigger_function_call, func_tool, func_tool_msg = llm_message
            
            if trigger_function_call:
                self.llm_task = asyncio.create_task(self.__execute_function_call(next_step=next_step, **data))
                return

            if latency:
                self.llm_latencies['turn_latencies'].append(latency)
            
            llm_response += data
            meta_info["end_of_llm_stream"] = end_of_llm_stream
            
            if self.stream:
                text_chunk = self.__process_stop_words(data, meta_info)
                await self._handle_llm_output(next_step, text_chunk, should_bypass_synth, meta_info)
            else:
                if end_of_llm_stream:
                    await self._handle_llm_output(next_step, llm_response, should_bypass_synth, meta_info)
        
        if end_of_llm_stream:
            self.history.append({'role': 'user', 'content': messages[-1]['content']})
            self.history.append({'role': 'assistant', 'content': llm_response})
            self.interim_history = copy.deepcopy(self.history)
            
            if self.use_llm_to_determine_hangup and not self.turn_based_conversation:
                completion_res = await self.tools["llm_agent"].check_for_completion(self.history, self.check_for_completion_prompt)
                if completion_res.get('hangup', 'No').lower() == "yes":
                    await self.process_call_hangup()
    
    async def __execute_function_call(self, url, method, param, api_token, model_args, meta_info, next_step, called_fun, **resp):
        self.check_if_user_online = False
        response = await trigger_api(url=url, method=method.lower(), param=param, api_token=api_token, meta_info=meta_info, run_id=self.run_id, **resp)
        
        self.history.append({"role": "assistant", "content": None, "tool_calls": resp["model_response"]})
        self.history.append({"role": "tool", "tool_call_id": resp.get("tool_call_id", ""), "content": str(response)})
        
        model_args["messages"] = self.history
        self.check_if_user_online = self.conversation_config.get("check_if_user_online", True)
        
        await self.__do_llm_generation(model_args["messages"], meta_info, next_step, should_bypass_synth=meta_info.get('bypass_synth', False), should_trigger_function_call=True)
        self.execute_function_call_task = None
        
    async def _listen_llm_input_queue(self):
        while True:
            try:
                ws_data_packet = await self.queues["llm"].get()
                meta_info = self.__get_updated_meta_info(ws_data_packet['meta_info'])
                bos_packet = create_ws_data_packet("<beginning_of_stream>", meta_info)
                await self.tools["output"].handle(bos_packet)
                await self._run_llm_task(create_ws_data_packet(ws_data_packet['data'], meta_info))
                eos_packet = create_ws_data_packet("<end_of_stream>", meta_info)
                await self.tools["output"].handle(eos_packet)
            except Exception as e:
                logger.error(f"Error in LLM input queue: {e}", exc_info=True)
                break

    async def _handle_transcriber_output(self, next_task, transcriber_message, meta_info):
        convert_to_request_log(message=transcriber_message, meta_info=meta_info, model="deepgram", run_id=self.run_id)
        if next_task == "llm":
            meta_info["origin"] = "transcriber"
            transcriber_package = create_ws_data_packet(transcriber_message, meta_info)
            self.llm_task = asyncio.create_task(self._run_llm_task(transcriber_package))
        else:
            logger.info("Next step after transcriber is not LLM, not implemented.")

    async def _listen_transcriber(self):
        try:
            while True:
                message = await self.transcriber_output_queue.get()
                if self.hangup_triggered:
                    if message.get("data") == "transcriber_connection_closed":
                        break
                    continue

                if message["data"] == "transcriber_connection_closed":
                    self.transcriber_duration += message.get("meta_info", {}).get("transcriber_duration", 0)
                    break
                
                if message.get("data") == "speech_started":
                    if self.tools["input"].welcome_message_played():
                        logger.info("User started speaking.")
                    continue
                
                transcript_data = message.get("data", {})
                if isinstance(transcript_data, dict):
                    if transcript_data.get("type") == "interim_transcript_received":
                        self.time_since_last_spoken_human_word = time.time()
                        if not self.tools["input"].welcome_message_played():
                            continue
                        if not self.callee_speaking:
                            self.callee_speaking = True
                        
                        transcript_len = len(transcript_data.get("content", "").strip().split())
                        if self.tools["input"].welcome_message_played() and transcript_len > self.number_of_words_for_interruption:
                            self.turn_id += 1
                            self.tools["input"].update_is_audio_being_played(False)
                            await self.__cleanup_downstream_tasks()

                    elif transcript_data.get("type") == "transcript":
                        self.callee_speaking = False
                        if self.output_task is None:
                            self.output_task = asyncio.create_task(self.__process_output_loop())
                        
                        transcriber_message = transcript_data.get("content", "")
                        meta_info = self.__get_updated_meta_info(message.get("meta_info", {}))
                        await self._handle_transcriber_output(self._get_next_step(meta_info.get("sequence"), "transcriber"), transcriber_message, meta_info)
        except Exception as e:
            logger.error(f"Error in transcriber listener: {e}", exc_info=True)

    async def _synthesize(self, message):
        meta_info = message["meta_info"]
        text = message["data"]
        meta_info["type"] = "audio"
        try:
            if not self.conversation_ended and ('is_first_message' in meta_info or message["meta_info"]["sequence_id"] in self.sequence_ids):
                convert_to_request_log(message=text, meta_info=meta_info, component="synthesizer", direction="request", model=self.synthesizer_provider, engine=self.tools['synthesizer'].get_engine(), run_id=self.run_id)
                self.synthesizer_characters += len(text)
                await self.tools["synthesizer"].push(message)
        except Exception as e:
            logger.error(f"Error in synthesizer: {e}", exc_info=True)

    async def __listen_synthesizer(self):
        try:
            while not self.conversation_ended:
                async for message in self.tools["synthesizer"].generate():
                    meta_info = message.get("meta_info", {})
                    sequence_id = meta_info.get("sequence_id")
                    if sequence_id in self.sequence_ids:
                        self.buffered_output_queue.put_nowait(message)
                        convert_to_request_log(
                            message=meta_info.get("text", ""), meta_info=meta_info, component="synthesizer",
                            direction="response", model=self.synthesizer_provider,
                            is_cached=meta_info.get("is_cached", False),
                            engine=self.tools['synthesizer'].get_engine(), run_id=self.run_id
                        )
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Synthesizer listener task cancelled.")
        except Exception as e:
            logger.error(f"Error in synthesizer listener: {e}", exc_info=True)
        finally:
            if "synthesizer" in self.tools:
                await self.tools["synthesizer"].cleanup()

    async def __process_output_loop(self):
        try:
            while True:
                message = await self.buffered_output_queue.get()
                if "sequence_id" in message.get("meta_info", {}) and message["meta_info"]["sequence_id"] in self.sequence_ids:
                    self.tools["input"].update_is_audio_being_played(True)
                    await self.tools["output"].handle(message)
                    if message['meta_info'].get("end_of_llm_stream"):
                        self.asked_if_user_is_still_there = False
                else:
                    logger.warning(f"Skipping message with stale sequence_id: {message['meta_info'].get('sequence_id')}")
        except Exception as e:
            logger.error(f'Error in processing message output: {e}', exc_info=True)

    async def __check_for_completion(self):
        while True:
            await asyncio.sleep(2)
            if self.hangup_triggered:
                break
            if self.tools["input"].is_audio_being_played_to_user():
                continue

            time_since_last_spoken_ai_word = time.time() - self.last_transmitted_timestamp
            if self.hang_conversation_after > 0 and time_since_last_spoken_ai_word > self.hang_conversation_after and self.time_since_last_spoken_human_word < self.last_transmitted_timestamp:
                logger.info(f"{time_since_last_spoken_ai_word:.2f}s of silence, hanging up.")
                await self.process_call_hangup()
                break
            elif time_since_last_spoken_ai_word > self.trigger_user_online_message_after and not self.asked_if_user_is_still_there and self.time_since_last_spoken_human_word < self.last_transmitted_timestamp:
                logger.info("Asking if user is still there.")
                self.asked_if_user_is_still_there = True
                if self.check_if_user_online:
                    meta_info = {'io': self.tools["output"].get_provider(), "request_id": str(uuid.uuid4()), "cached": False, "sequence_id": -1, 'format': 'pcm', 'end_of_llm_stream': True}
                    await self._synthesize(create_ws_data_packet(self.check_user_online_message, meta_info=meta_info))
                await self.tools["output"].handle_interruption()
    
    async def process_call_hangup(self):
        if self.call_hangup_message:
            await self.wait_for_current_message()
            await self.__cleanup_downstream_tasks()
            meta_info = {'io': self.tools["output"].get_provider(), "request_id": str(uuid.uuid4()),
                         "cached": False, "sequence_id": -1, 'format': 'pcm', 'message_category': 'agent_hangup',
                         'end_of_llm_stream': True}
            self.hangup_triggered = True
            await self._synthesize(create_ws_data_packet(self.call_hangup_message, meta_info=meta_info))
        else:
            await self.__process_end_of_conversation()

    async def __first_message(self, timeout=10.0):
        start_time = asyncio.get_running_loop().time()
        text_to_send = self.kwargs.get('agent_welcome_message', "")
        
        if not text_to_send:
            return

        while True:
            elapsed_time = asyncio.get_running_loop().time() - start_time
            if elapsed_time > timeout:
                await self.__process_end_of_conversation()
                break

            if self.default_io:
                meta_info = {'io': 'default', 'is_first_message': True, "request_id": str(uuid.uuid4()), "cached": True, "sequence_id": -1, 'format': 'wav', 'text': text_to_send, 'end_of_llm_stream': True}
                await self._synthesize(create_ws_data_packet(text_to_send, meta_info=meta_info))
                break
            
            stream_sid = self.tools["input"].get_stream_sid()
            if stream_sid:
                meta_info = {'io': self.tools["output"].get_provider(), 'message_category': 'agent_welcome_message', 'stream_sid': stream_sid, "request_id": str(uuid.uuid4()), "cached": True, "sequence_id": -1, 'format': self.task_config["tools_config"]["output"]["format"], 'text': text_to_send, 'end_of_llm_stream': True}
                await self._synthesize(create_ws_data_packet(text_to_send, meta_info=meta_info))
                break
            await asyncio.sleep(0.1)

    async def handle_init_event(self, init_meta_data):
        try:
            if 'recipient_data' in self.context_data:
                self.context_data["recipient_data"].update(init_meta_data.get("context_data", {}))
            else:
                self.context_data["recipient_data"] = init_meta_data.get("context_data", {})
                
            self.prompts["system_prompt"] = update_prompt_with_context(self.prompts.get("system_prompt", ""), self.context_data)
            if self.system_prompt.get('content'):
                self.system_prompt['content'] = update_prompt_with_context(self.system_prompt['content'], self.context_data)
                self.history[0]['content'] = self.system_prompt['content']
            
            self.kwargs["agent_welcome_message"] = update_prompt_with_context(self.kwargs.get("agent_welcome_message", ""), self.context_data)
            if len(self.history) > 1 and self.history[1].get("role") == "assistant":
                self.history[1]["content"] = self.kwargs["agent_welcome_message"]
            
            await self.tools["output"].send_init_acknowledgement()
            self.first_message_task = asyncio.create_task(self.__first_message())
        except Exception as e:
            logger.error(f"Error in handle_init_event: {e}", exc_info=True)

    async def run(self):
        try:
            if self._is_conversation_task():
                tasks = [asyncio.create_task(self.tools['input'].handle())]
                if not self.is_web_based_call:
                    self.first_message_task = asyncio.create_task(self.__first_message())
                
                if "transcriber" in self.tools:
                    tasks.append(asyncio.create_task(self._listen_transcriber()))
                    self.transcriber_task = asyncio.create_task(self.tools["transcriber"].run())

                if self.turn_based_conversation:
                    self.llm_queue_task = asyncio.create_task(self._listen_llm_input_queue())
                
                if "synthesizer" in self.tools and not self.turn_based_conversation:
                    self.synthesizer_task = asyncio.create_task(self.__listen_synthesizer())

                self.output_task = asyncio.create_task(self.__process_output_loop())
                
                if not self.turn_based_conversation or self.enforce_streaming:
                    self.hangup_task = asyncio.create_task(self.__check_for_completion())
                
                await asyncio.gather(*tasks)

            else: # Extraction, Summarization, etc.
                await self._run_llm_task(self.input_parameters)

        except asyncio.CancelledError:
            await self.handle_cancellation("Task manager run cancelled.")
        except Exception as e:
            await self.handle_cancellation(f"Exception in TaskManager run: {e}")
            raise e
        finally:
            tasks_to_cancel = [
                self.synthesizer_task, self.synthesizer_monitor_task, self.output_task,
                self.hangup_task, self.backchanneling_task, self.ambient_noise_task,
                self.first_message_task, self.handle_accumulated_message_task
            ]
            await asyncio.gather(*[process_task_cancellation(task, str(i)) for i, task in enumerate(tasks_to_cancel)], return_exceptions=True)
            
            if self._is_conversation_task():
                output = {
                    "messages": self.history,
                    "conversation_time": time.time() - self.start_time,
                    "transcriber_duration": self.transcriber_duration,
                    "synthesizer_characters": self.tools.get('synthesizer').get_synthesized_characters() if self.tools.get('synthesizer') else 0,
                    "ended_by_assistant": self.ended_by_assistant
                }
                if self.should_record:
                    output['recording_url'] = await save_audio_file_to_s3(self.conversation_recording, self.sampling_rate, self.assistant_id, self.run_id)
                return output
            else:
                output = self.input_parameters
                if self.task_config["task_type"] == "extraction":
                    return {"extracted_data": self.extracted_data, "task_type": "extraction"}
                elif self.task_config["task_type"] == "summarization":
                    return {"summary": self.summarized_data, "task_type": "summarization"}
                elif self.task_config["task_type"] == "webhook":
                    return {"status": self.webhook_response, "task_type": "webhook"}
                return output

    async def handle_cancellation(self, message):
        logger.warning(f"Handling cancellation: {message}")
        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error during task cancellation: {e}")