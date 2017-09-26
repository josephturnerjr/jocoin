import json

def default_serializer(obj):
    try:
        return obj.as_json()
    except:
        raise TypeError()
        
def serialize(obj):
    return json.dumps(obj, default=default_serializer)

def fmt_h(h):
    return str(h)[:6] + "..."
