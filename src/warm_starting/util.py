from Box2D import (b2World)
from Box2D import (b2FixtureDef)
from Box2D import (b2Vec2)

# Creates a copy of the given world by creating copies of all bodies
def copyWorld(world):
    copy = b2World(world.gravity)

    for body in world.bodies:
        fixtures = []
        for fixture in body.fixtures:
            fixtures.append(b2FixtureDef(shape=fixture.shape, density=fixture.density))

        copy.CreateBody(type=body.type, fixtures=fixtures, userData=body.userData,
                        position=b2Vec2(body.position.x, body.position.y), angle=body.angle,
                        linearVelocity=b2Vec2(body.linearVelocity.x, body.linearVelocity.y),
                        angularVelocity=body.angularVelocity)

    return copy