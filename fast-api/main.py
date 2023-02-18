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
    host="redis-16169.c293.eu-central-1-1.ec2.cloud.redislabs.com",
    port=16169,
    password="SPTzjyDiawPKNjDo0Fvhf8lXFzFsP8KQ",
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
     
@app.get('/deliveries/{pk}/status')
async def get_state(pk: str):
     #we get the state from the cache
     state = redis.get(f'delivery:{pk}')
     return json.loads(state)


@app.post('/deliveries/create')
async def create(request: Request):
     body = await request.json()
     delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
     event = Event(delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()
     state = consumers.create_delivery({}, event)
     #when we create the state we will store it in the cache
     redis.set(f'delivery:{delivery.pk}', json.dumps(state))
     #and we returned it
     return state


@app.post('/event')
async def dispatch(request: Request):
     body = await request.json()
     delivery_id = body['delivery_id']
     event = Event(delivery_id=delivery_id, type=body['type'], data=json.dumps(body['data'])).save()
     state = await get_state(delivery_id)
     new_state = consumers.start_delivery(state, event)
     redis.set(f'delivery: {delivery_id}', json.dumps(new_state))