from flask import Flask, render_template, request, jsonify
import json
from typing import Dict, List, Optional, Any


app = Flask(__name__)

#zapato


# ESTRUCTURAS DE DATOS PRINCIPALES




class GraphData:
    """
    Clase que maneja los datos del grafo de tareas.
   
    """
   
    def __init__(self):
        """
        Inicializa las estructuras de datos principales.
       
        - nodes_dict: Diccionario que mapea ID de nodo -> propiedades del nodo
        - edges_dict: Diccionario que mapea ID de arista -> propiedades de la arista
        - node_counter: Contador para asignar IDs únicos a los nodos
        - edge_counter: Contador para asignar IDs únicos a las aristas
        """
        self.nodes_dict: Dict[int, Dict[str, Any]] = {}
        self.edges_dict: Dict[int, Dict[str, Any]] = {}
        self.node_counter: int = 1
        self.edge_counter: int = 1
   
    def get_nodes_list(self) -> List[Dict[str, Any]]:
        """
        Convierte el diccionario de nodos a una lista para compatibilidad con el frontend.
       
        Returns:
            List[Dict]: Lista de nodos con todas sus propiedades
        """
        return list(self.nodes_dict.values())
   
    def get_edges_list(self) -> List[Dict[str, Any]]:
        """
        Convierte el diccionario de aristas a una lista para compatibilidad con el frontend.
       
        Returns:
            List[Dict]: Lista de aristas con todas sus propiedades
        """
        return list(self.edges_dict.values())
   
    def add_node(self, name: str, x: float = 100, y: float = 100) -> Dict[str, Any]:
        """
        Añade un nuevo nodo al grafo.
       
        Args:
            name (str): Nombre del nodo/tarea
            x (float): Posición X en el canvas (default: 100)
            y (float): Posición Y en el canvas (default: 100)
       
        Returns:
            Dict[str, Any]: El nodo creado con todas sus propiedades
        """
        node_properties = {
            'id': self.node_counter,
            'name': name,
            'x': x,
            'y': y,
            'created_at': None,  # Se puede añadir timestamp si es necesario
            'metadata': {}       # Para futuras extensiones
        }
       
        self.nodes_dict[self.node_counter] = node_properties
        self.node_counter += 1
       
        return node_properties
   
    def update_node(self, node_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza las propiedades de un nodo existente.
       
        Args:
            node_id (int): ID del nodo a actualizar
            updates (Dict[str, Any]): Diccionario con las propiedades a actualizar
       
        Returns:
            Optional[Dict[str, Any]]: El nodo actualizado o None si no existe
        """
        if node_id in self.nodes_dict:
            self.nodes_dict[node_id].update(updates)
            return self.nodes_dict[node_id]
        return None
   
    def delete_node(self, node_id: int) -> bool:
        """
        Elimina un nodo y todas sus aristas asociadas.
       
        Args:
            node_id (int): ID del nodo a eliminar
       
        Returns:
            bool: True si se eliminó correctamente, False si no existía
        """
        if node_id in self.nodes_dict:
            # Eliminar el nodo
            del self.nodes_dict[node_id]
           
            # Eliminar todas las aristas que conectan con este nodo
            edges_to_remove = [
                edge_id for edge_id, edge in self.edges_dict.items()
                if edge['from'] == node_id or edge['to'] == node_id
            ]
           
            for edge_id in edges_to_remove:
                del self.edges_dict[edge_id]
           
            return True
        return False
   
    def add_edge(self, from_node: int, to_node: int, duration: float = 0,
                 cost: float = 0, prerequisites: str = '',
                 postrequisites: str = '') -> Optional[Dict[str, Any]]:
        """
        Añade una nueva arista entre dos nodos.
       
        Args:
            from_node (int): ID del nodo origen
            to_node (int): ID del nodo destino
            duration (float): Duración de la tarea (default: 0)
            cost (float): Costo de la tarea (default: 0)
            prerequisites (str): Prerrequisitos de la tarea (default: '')
            postrequisites (str): Postrequisitos de la tarea (default: '')
       
        Returns:
            Optional[Dict[str, Any]]: La arista creada o None si los nodos no existen
        """
        # Verificar que ambos nodos existen
        if from_node not in self.nodes_dict or to_node not in self.nodes_dict:
            return None
       
        edge_properties = {
            'id': self.edge_counter,
            'from': from_node,
            'to': to_node,
            'duration': duration,
            'cost': cost,
            'prerequisites': prerequisites,
            'postrequisites': postrequisites,
            'weight': duration,  # Se puede usar para algoritmos de caminos
            'metadata': {}       # Para futuras extensiones
        }
       
        self.edges_dict[self.edge_counter] = edge_properties
        self.edge_counter += 1
       
        return edge_properties
   
    def update_edge(self, edge_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza las propiedades de una arista existente.
       
        Args:
            edge_id (int): ID de la arista a actualizar
            updates (Dict[str, Any]): Diccionario con las propiedades a actualizar
       
        Returns:
            Optional[Dict[str, Any]]: La arista actualizada o None si no existe
        """
        if edge_id in self.edges_dict:
            self.edges_dict[edge_id].update(updates)
            # Actualizar weight si se modificó duration
            if 'duration' in updates:
                self.edges_dict[edge_id]['weight'] = updates['duration']
            return self.edges_dict[edge_id]
        return None
   
    def delete_edge(self, edge_id: int) -> bool:
        """
        Elimina una arista del grafo.
       
        Args:
            edge_id (int): ID de la arista a eliminar
       
        Returns:
            bool: True si se eliminó correctamente, False si no existía
        """
        if edge_id in self.edges_dict:
            del self.edges_dict[edge_id]
            return True
        return False
   
    def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un nodo por su ID.
       
        Args:
            node_id (int): ID del nodo
       
        Returns:
            Optional[Dict[str, Any]]: El nodo o None si no existe
        """
        return self.nodes_dict.get(node_id)
   
    def get_edge_by_id(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una arista por su ID.
       
        Args:
            edge_id (int): ID de la arista
       
        Returns:
            Optional[Dict[str, Any]]: La arista o None si no existe
        """
        return self.edges_dict.get(edge_id)
   
    def clear_all(self) -> None:
        """
        Limpia todos los nodos y aristas del grafo.
        """
        self.nodes_dict.clear()
        self.edges_dict.clear()
        self.node_counter = 1
        self.edge_counter = 1


# Instancia global para manejar los datos del grafo
graph_data = GraphData()


# ========================================
# RUTAS DE LA APLICACIÓN
# ========================================


@app.route('/')
def index() -> str:
    """
    Ruta principal que renderiza la interfaz HTML del gestor de grafos.
   
    Returns:
        str: Template HTML renderizado
    """
    return render_template('index.html')


@app.route('/api/nodes', methods=['GET', 'POST'])
def handle_nodes():
    """
    Maneja las operaciones GET y POST para nodos.
   
    GET: Retorna todos los nodos del grafo
    POST: Crea un nuevo nodo con los datos proporcionados
   
    Returns:
        JSON: Lista de nodos (GET) o nodo creado (POST)
    """
    if request.method == 'GET':
        # Retornar todos los nodos como lista
        nodes_list = graph_data.get_nodes_list()
        return jsonify(nodes_list)
   
    elif request.method == 'POST':
        # Obtener datos del request
        data = request.get_json()
       
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
       
        # Validar que se proporcione al menos el nombre
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'El nombre del nodo es requerido'}), 400
       
        # Crear nuevo nodo
        new_node = graph_data.add_node(
            name=name,
            x=data.get('x', 100),
            y=data.get('y', 100)
        )
       
        return jsonify(new_node), 201


@app.route('/api/nodes/<int:node_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_node(node_id: int):
    """
    Maneja operaciones específicas para un nodo individual.
   
    Args:
        node_id (int): ID del nodo a operar
   
    GET: Retorna información del nodo específico
    PUT: Actualiza las propiedades del nodo
    DELETE: Elimina el nodo y sus aristas asociadas
   
    Returns:
        JSON: Nodo solicitado/actualizado o mensaje de confirmación
    """
    if request.method == 'GET':
        # Obtener nodo específico
        node = graph_data.get_node_by_id(node_id)
        if node:
            return jsonify(node)
        else:
            return jsonify({'error': 'Nodo no encontrado'}), 404
   
    elif request.method == 'PUT':
        # Actualizar nodo existente
        data = request.get_json()
       
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
       
        updated_node = graph_data.update_node(node_id, data)
       
        if updated_node:
            return jsonify(updated_node)
        else:
            return jsonify({'error': 'Nodo no encontrado'}), 404
   
    elif request.method == 'DELETE':
        # Eliminar nodo
        success = graph_data.delete_node(node_id)
       
        if success:
            return jsonify({'success': True, 'message': 'Nodo eliminado correctamente'})
        else:
            return jsonify({'error': 'Nodo no encontrado'}), 404


@app.route('/api/edges', methods=['GET', 'POST'])
def handle_edges():
    """
    Maneja las operaciones GET y POST para aristas.
   
    GET: Retorna todas las aristas del grafo
    POST: Crea una nueva arista con los datos proporcionados
   
    Returns:
        JSON: Lista de aristas (GET) o arista creada (POST)
    """
    if request.method == 'GET':
        # Retornar todas las aristas como lista
        edges_list = graph_data.get_edges_list()
        return jsonify(edges_list)
   
    elif request.method == 'POST':
        # Obtener datos del request
        data = request.get_json()
       
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
       
        # Validar nodos origen y destino
        from_node = data.get('from')
        to_node = data.get('to')
       
        if from_node is None or to_node is None:
            return jsonify({'error': 'Se requieren nodos origen y destino'}), 400
       
        # Crear nueva arista
        new_edge = graph_data.add_edge(
            from_node=from_node,
            to_node=to_node,
            duration=float(data.get('duration', 0)),
            cost=float(data.get('cost', 0)),
            prerequisites=data.get('prerequisites', ''),
            postrequisites=data.get('postrequisites', '')
        )
       
        if new_edge:
            return jsonify(new_edge), 201
        else:
            return jsonify({'error': 'No se pudo crear la arista. Verifica que los nodos existan'}), 400


@app.route('/api/edges/<int:edge_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_edge(edge_id: int):
    """
    Maneja operaciones específicas para una arista individual.
   
    Args:
        edge_id (int): ID de la arista a operar
   
    GET: Retorna información de la arista específica
    PUT: Actualiza las propiedades de la arista
    DELETE: Elimina la arista
   
    Returns:
        JSON: Arista solicitada/actualizada o mensaje de confirmación
    """
    if request.method == 'GET':
        # Obtener arista específica
        edge = graph_data.get_edge_by_id(edge_id)
        if edge:
            return jsonify(edge)
        else:
            return jsonify({'error': 'Arista no encontrada'}), 404
   
    elif request.method == 'PUT':
        # Actualizar arista existente
        data = request.get_json()
       
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
       
        # Convertir valores numéricos si están presentes
        if 'duration' in data:
            data['duration'] = float(data['duration'])
        if 'cost' in data:
            data['cost'] = float(data['cost'])
       
        updated_edge = graph_data.update_edge(edge_id, data)
       
        if updated_edge:
            return jsonify(updated_edge)
        else:
            return jsonify({'error': 'Arista no encontrada'}), 404
   
    elif request.method == 'DELETE':
        # Eliminar arista
        success = graph_data.delete_edge(edge_id)
       
        if success:
            return jsonify({'success': True, 'message': 'Arista eliminada correctamente'})
        else:
            return jsonify({'error': 'Arista no encontrada'}), 404


@app.route('/api/graph/clear', methods=['POST'])
def clear_graph():
    """
    Limpia todo el grafo (todos los nodos y aristas).
   
    Returns:
        JSON: Mensaje de confirmación
    """
    graph_data.clear_all()
    return jsonify({'success': True, 'message': 'Grafo limpiado correctamente'})


@app.route('/api/graph/stats', methods=['GET'])
def get_graph_stats():
    """
    Obtiene estadísticas básicas del grafo.
   
    Returns:
        JSON: Diccionario con estadísticas del grafo
    """
    stats = {
        'total_nodes': len(graph_data.nodes_dict),
        'total_edges': len(graph_data.edges_dict),
        'next_node_id': graph_data.node_counter,
        'next_edge_id': graph_data.edge_counter,
        'total_cost': sum(edge.get('cost', 0) for edge in graph_data.edges_dict.values()),
        'total_duration': sum(edge.get('duration', 0) for edge in graph_data.edges_dict.values())
    }
   
    return jsonify(stats)


# ========================================
# MANEJO DE ERRORES
# ========================================


@app.errorhandler(404)
def not_found(error):
    """
    Maneja errores 404 (No encontrado).
   
    Returns:
        JSON: Mensaje de error personalizado
    """
    return jsonify({'error': 'Recurso no encontrado'}), 404


@app.errorhandler(400)
def bad_request(error):
    """
    Maneja errores 400 (Solicitud incorrecta).
   
    Returns:
        JSON: Mensaje de error personalizado
    """
    return jsonify({'error': 'Solicitud incorrecta'}), 400


@app.errorhandler(500)
def internal_error(error):
    """
    Maneja errores 500 (Error interno del servidor).
   
    Returns:
        JSON: Mensaje de error personalizado
    """
    return jsonify({'error': 'Error interno del servidor'}), 500


# ========================================
# PUNTO DE ENTRADA
# ========================================


if __name__ == '__main__':
   
    app.run(
        debug=True,      # Modo debug para desarrollo
        host='0.0.0.0',  # Accesible desde cualquier IP
        port=5000        # Puerto estándar de Flask
    )
