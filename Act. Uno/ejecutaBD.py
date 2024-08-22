from utils import conexionBD
import json

#ejecutar store con parametros
params = ('ABA')
result = conexionBD.execute_sql_storeProcedure("exec spClientes_ObtenClientesPorNombre @pNombre = ?", params);
print(result)

def query_empresa(query):
        if not query:
            return json.dumps({"status": "success", "message": "hubo un query"})
        result = []
        search = (query.get("NombreCliente", ""))
        print(search)
        result = conexionBD.execute_sql_storeProcedure("exec spClientes_ObtenClientesPorNombre @pNombre = ?", search)
        print(result)
        return json.dumps({"status": "success", "message": result})