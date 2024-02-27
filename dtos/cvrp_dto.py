from typing import Tuple
from pydantic import BaseModel
from typing import Optional, List

class AddressDto(BaseModel):
    id: Optional[int] = None  
    formatted_address: str
    street_name: str
    street_number: str
    city: str
    postal_code: str
    neighborhood: str
    state: str
    complement: str
    latitude: float
    longitude: float
    
class OrderDto(BaseModel):
    id: Optional[int] = None
    volume: float
    address: AddressDto
    
class RouteDto(BaseModel):
    id: Optional[int] = None
    orders: List[OrderDto]
    street_route: List[Tuple[float, float]]
    total_volume: float
    
class VrpInDto(BaseModel):
    id: Optional[int] = None
    orders: List[OrderDto]
    drivers_volume: float
    
class VrpOutDto(BaseModel):
    id: Optional[int] = None
    routes: List[RouteDto]
    drivers_volume: float
    
    
class GraphStatsDto(BaseModel):
    id: Optional[int] = None
    distances_matrix: str
    seconds_to_calculate: float

class GeneticAlgorithmStatsDto(BaseModel):
    id: Optional[int] = None
    processor_type: str
    final_generation: int
    final_fitness: float
    population_size: int
    mutation_rate: float
    seconds_processed: float
    converge: bool
    graph_stats: GraphStatsDto