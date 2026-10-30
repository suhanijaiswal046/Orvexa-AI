"""Safe Pandas analytics over an uploaded CSV (no arbitrary code execution)."""
import pandas as pd
from src.schemas import AnalyticsRequest

def analyze_csv(file_or_path, question: str, llm) -> tuple[str, pd.DataFrame | None]:
    df = pd.read_csv(file_or_path)
    if df.empty:
        return "The uploaded CSV has no rows.", None
    schema = {str(c): str(df[c].dtype) for c in df.columns}
    prompt = f"""Choose one supported operation for this CSV question.
Operations: overview, sum, mean, max, min, top, value_counts, correlation.
Return only the structured request. Use exact column names from this schema.
For top, set column to the numeric column and group_by optionally to a category.
Question: {question}
CSV schema: {schema}
"""
    request: AnalyticsRequest = llm.with_structured_output(AnalyticsRequest).invoke(prompt)
    op, col, group = request.operation, request.column, request.group_by
    if op == "overview":
        return f"Rows: {len(df)}\nColumns: {len(df.columns)}\n\n{df.describe(include='all').fillna('').to_string()}", df.head(20)
    if op == "correlation":
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] < 2:
            return "Correlation requires at least two numeric columns.", None
        return numeric.corr().round(3).to_string(), numeric.corr().round(3)
    if not col or col not in df.columns:
        return f"I couldn't identify a valid column. Available columns: {', '.join(map(str, df.columns))}", None
    if op in {"sum", "mean", "max", "min"}:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return f"Column '{col}' is not numeric, so {op} cannot be calculated.", None
        value = getattr(df[col], op)()
        return f"{op.title()} of '{col}': {value:,.3f}", None
    if op == "value_counts":
        result = df[col].value_counts().head(request.top_n)
        return f"Top values in '{col}':\n{result.to_string()}", result.rename("count").to_frame()
    if op == "top":
        if not pd.api.types.is_numeric_dtype(df[col]):
            return f"Column '{col}' must be numeric for top ranking.", None
        if group and group in df.columns:
            result = df.groupby(group, dropna=False)[col].sum().sort_values(ascending=False).head(request.top_n)
        else:
            result = df.nlargest(request.top_n, col)[[col]]
        return f"Top results for '{col}':\n{result.to_string()}", result.to_frame() if isinstance(result, pd.Series) else result
    return "I could not perform that analysis.", None
