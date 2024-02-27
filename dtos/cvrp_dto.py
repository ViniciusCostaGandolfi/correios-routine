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
    distribuitor: AddressDto
    orders: List[OrderDto]
    drivers_volume: float
    
class VrpOutDto(BaseModel):
    id: Optional[int] = None
    distribuitor: AddressDto
    routes: List[RouteDto]
    drivers_volume: float
    
    
class GraphStatsDto(BaseModel):
    id: Optional[int] = None
    distances_matrix: str
    seconds_to_calculate: float

class GeneticAlgorithmStatsDto(BaseModel):
    id: Optional[int] = None
    processor_type: str
    plot_fitness: List[float]
    plot_generations: List[float]
    plot_times: List[float]
    population_size: int
    mutation_rate: float
    converge: bool
    graph_stats: GraphStatsDto