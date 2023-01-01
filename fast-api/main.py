from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import json 

app = FastAPI()

# add the midelware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# instruction pour connecter a redis cloud 
redis = get_redis_connection(
    host="redis-12587.c250.eu-central-1-1.ec2.cloud.redislabs.com",
    port=12587,
    password="O2fzOTjuFjcFzCPLm5ZK6OfI4uTLcBrP",
    decode_responses=True,
)

# creation class delivery
class Delivery(HashModel):
    budget: int = 0
    notes: str  = '' 
    # class meta to connect this model with redis database
    
    class Meta :
        database = redis
        
#
class Event(HashModel):
    delivery_id: str = None
    type: str  
    data: str 
    # class meta to connect this model with redis database
    
    class Meta :
        database = redis
        
@app.post('/deliveries/create')
async def create(request: Request):
    body = await request.json()
    delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
    event = Event(delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()
    return event

