from google.cloud import datastore

# 初始化 Datastore 客户端
datastore_client = datastore.Client()

def save_car_data(car_number, status, unit):
    key = datastore_client.key('Car', car_number)
    entity = datastore.Entity(key)
    entity.update({
        'status': status,
        'unit': unit
    })
    datastore_client.put(entity)

def get_car_data(car_number):
    key = datastore_client.key('Car', car_number)
    entity = datastore_client.get(key)
    return entity

def get_all_cars():
    query = datastore_client.query(kind='Car')
    return list(query.fetch())

def get_cars_by_status(status):
    query = datastore_client.query(kind='Car')
    query.add_filter('status', '=', status)
    return list(query.fetch())

def get_cars_by_unit(unit):
    query = datastore_client.query(kind='Car')
    query.add_filter('unit', '=', unit)
    return list(query.fetch())