from uuid import uuid4

from pydantic import BaseModel, Field

from langchain_core.tools import tool, BaseTool


class Table(BaseModel):
    header: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)

class ParserLlmToolManager:
    def __init__(self):
        self.tables: dict[str, Table] = {}
    
    def _get_table(self, table_id: str) -> Table:
        table = self.tables.get(table_id)
        if table is None:
            raise ValueError(f"Table not found: {table_id}")
        return table

    def get_tools(self) -> list[BaseTool]:
        
        @tool("create_table")
        def create_table() -> str:
            """Create an empty table and return its table_id."""
            table_id = str(uuid4())
            self.tables[table_id] = Table()
            return table_id
        

        @tool("add_header")
        def add_header(table_id: str, header: list[str]) -> str:
            """Set the header row for a table."""
            table = self._get_table(table_id)
            table.header = [str(cell) for cell in header]            
            return "header added"

        @tool("add_row")
        def add_row(table_id: str, row: list[str]) -> str:
            """Append a row to a table."""
            table = self._get_table(table_id)
            table.rows.append([str(cell) for cell in row])
            return "row added"


        @tool("get_table")
        def get_table(table_id: str) -> Table:
            """Return a table by id with the shape {'header': [...], 'rows': [[...]]}."""
            return self._get_table(table_id)


        @tool("list_tables")
        def list_tables() -> dict[str, list[Table]]:
            """Return all created tables with the shape {'tables': [{'header': [...], 'rows': [[...]]}]}."""
            return {"tables": list(self.tables.values())}
        

        return [
            list_tables,
            get_table,
            create_table,
            add_header,
            add_row,
        ]


    # public api 
    def get_output(self) -> dict[str, list[dict[str, list[str] | list[list[str]]]]]:
        """Return tool outputs as JSON-ready data."""
        return {
            "tables": [table.model_dump() for table in self.tables.values()]
        }
