from main import app

# Vercel necesita esta estructura
def handler(event, context):
    return app

# También exportamos la app directamente
application = app