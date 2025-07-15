# backend/chart_generator.py
def create_chart(chart_type: str, x_axis: str, y_axis: str) -> str:
    if chart_type == "line":
        code = (
            "import plotly.express as px\n"
            f"fig = px.line(x=df['{x_axis}'], y=df['{y_axis}'], title='Line Chart')\n"
            "fig.update_layout(xaxis_title='{x_axis}', yaxis_title='{y_axis}', xaxis_tickangle=-45)\n"
            "fig.show()"
        )
    elif chart_type == "bar":
        code = (
            "import plotly.express as px\n"
            f"fig = px.bar(x=df['{x_axis}'], y=df['{y_axis}'], title='Bar Chart')\n"
            "fig.update_layout(xaxis_title='{x_axis}', yaxis_title='{y_axis}')\n"
            "fig.show()"
        )
    elif chart_type == "pie":
        code = (
            "import plotly.express as px\n"
            f"fig = px.pie(names=df['{x_axis}'], values=df['{y_axis}'], title='Pie Chart')\n"
            "fig.show()"
        )
    elif chart_type == "scatter":
        code = (
            "import plotly.express as px\n"
            f"fig = px.scatter(x=df['{x_axis}'], y=df['{y_axis}'], title='Scatter Plot')\n"
            "fig.update_layout(xaxis_title='{x_axis}', yaxis_title='{y_axis}')\n"
            "fig.show()"
        )
    elif chart_type == "heatmap":
        code = (
            "import plotly.express as px\n"
            f"fig = px.density_heatmap(x=df['{x_axis}'], y=df['{y_axis}'], title='Heatmap')\n"
            "fig.update_layout(xaxis_title='{x_axis}', yaxis_title='{y_axis}')\n"
            "fig.show()"
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return code