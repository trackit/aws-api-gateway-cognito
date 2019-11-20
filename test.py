import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def generate_response(status, body, headers={}):
    return {
        "statusCode": status,
        "body": json.dumps(body, indent=4, cls=DecimalEncoder),
        "headers": headers
    }


def endpoint_test(event, context):
    return generate_response(200, {"status": True})


def endpoint_test_auth(event, context):
    return generate_response(200, {"Hello world": True})
