from wecs.core import Component, System, and_filter
from panda3d import core
from dataclasses import field

from .terrain import TerrainObject


@Component()
class Collider:
    solid: core.CollisionSolid
    from_mask: int = 0
    into_mask: int = 1


class CollisionDetectionSystem(System):
    entity_filters = {
        'collider': and_filter([Collider]),
    }

    def __init__(self):
        System.__init__(self)

        self.traverser = core.CollisionTraverser()
        #self.traverser.show_collisions(base.render)

        self.handler = core.CollisionHandlerEvent()
        self.handler.add_in_pattern('%fn-into-%in')

    def init_entity(self, filter, entity):
        collider = entity[Collider]
        path = entity[TerrainObject]._root

        cnode = core.CollisionNode(entity._uid.name)
        cnode.add_solid(collider.solid)
        cnode.set_from_collide_mask(collider.from_mask)
        cnode.set_into_collide_mask(collider.into_mask)
        cpath = path.attach_new_node(cnode)
        #cpath.show()

        cnode.set_python_tag('entity', entity)

        if collider.from_mask:
            self.traverser.add_collider(cpath, self.handler)

    def update(self, entities_by_filter):
        self.traverser.traverse(base.render)
