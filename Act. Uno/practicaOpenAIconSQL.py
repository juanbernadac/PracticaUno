from openai import OpenAI
from conexiones import conexionOpenAi
import ejecutaBD
import json

class OpenAIAssistant:
    def __init__(self, question_user):
        self.client = OpenAI(api_key= conexionOpenAi.api_key)
        #Lista de mensajes guardados en el hilo
        self.messages = [
                {"role": "system", "content": "Eres un empleado bilingüe de EISEI que ayuda a los clientes con información de los reportes de oportunidad. Tu función es brindar información clara sobre los reportes de oportunidad, no buscas informacion en internet ni nada que no sea de la empresa EISEI." },
        ]
        
        self.messages.append({"role": "user", "content": question_user})

    def get_response(self):
            #estructura para generar respuesta que genera openai 
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                tools=[
                    {
                            "type": "function",
                            "function": {
                                "name": "query_empresa",
                                "description": "Query the company ID based on its name and return a type of report, either weekly or daily, as requested by the user.",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "description": "The JSON data to query",
                                            "items": {
                                                "type": "object"
                                            }
                                        },
                                        "query": {
                                            "type": "object",
                                            "description": "The query parameters",
                                            "properties": {
                                                "NombreCliente": {"type": "string"},
                                                "RFC_Cliente": {"type": "string"}
                                            }
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        }
                    ],
                tool_choice="auto"
            )
            #respuesta completa generada
            response_message = response.choices[0].message

            #recolectar las funciones de las respuestas
            tool_calls = response_message.tool_calls
            print('tool calls')
            print(tool_calls)

            #si hay llamada a la funcion
            if tool_calls:
                available_functions = {
                    "query_empresa": ejecutaBD.query_empresa, #mapea las funciones a las funciones de la base de datos
                }
                print('available functions')
                print(available_functions)
                self.messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name #obtiene el nombre de la funcion que se llamo
                    function_to_call = available_functions[function_name] #busca la funcion asignada la clase de Database
                    function_args = json.loads(tool_call.function.arguments)
                    print('function_args')
                    print(function_args)
                    if function_name == "query_empresa":
                        #va a la funcion de query_empresa en la clase DataBase y ejecuta la funcion 
                        print('function_args query')
                        print(function_args.get("query"))
                        function_response = function_to_call( 
                            query= function_args.get("query") 
                        )
                self.messages.append( #agrega a la lista de mensajes la respuesta a esa funcion por medio de su id
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                            
                        }
                    )
                #genera una respuesta en base a lo que se contesto en la funcion
                second_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=self.messages,
                )
                #regresa al usuario esa respuesta
                if second_response.choices:
                    return second_response.choices[0].message.content
            #si no se llaman funciones genera una repsuesta normal
            else:
                print(response_message)
                return response_message.content            
