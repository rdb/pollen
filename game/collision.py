from wecs.core import Component, System, and_filter
from panda3d import core
from dataclasses import field

from .terrain import TerrainObject


GRAVITY = 1.0


@Component()
class Collider:
    solid: core.CollisionSolid = None
    from_mask: int = 0
    into_mask: int = 1
    tangible: bool = True
    bury: float = 0.0


class CollisionDetectionSystem(System):
    entity_filters = {
        'collider': and_filter([Collider]),
    }

    def __init__(self):
        System.__init__(self)

        self.traverser = core.CollisionTraverser()
        #self.traverser.show_collisions(base.render)

        self.handler = core.CollisionHandlerPusher()
        self.handler.add_in_pattern('%fn-into-%in')
        self.handler.horizontal = False

        self.player_obj = None

    def init_entity(self, filter, entity):
        collider = entity[Collider]
        path = entity[TerrainObject]._root

        if not collider.solid:
            bounds = path.get_child(0).get_bounds()
            bury = collider.bury
            collider.solid = core.CollisionSphere(bounds.center - (0, 0, bury), bounds.radius * 0.5 + bury)

        collider.solid.tangible = collider.tangible

        cnode = core.CollisionNode(entity._uid.name)
        cnode.add_solid(collider.solid)
        cnode.set_from_collide_mask(collider.from_mask)
        cnode.set_into_collide_mask(collider.into_mask)
        cpath = path.attach_new_node(cnode)
        #cpath.show()

        cnode.set_python_tag('entity', entity)

        if collider.from_mask:
            self.traverser.add_collider(cpath, self.handler)

            if collider.tangible:
                self.handler.add_collider(cpath, path)
                self.player_obj = entity[TerrainObject]

    def update(self, entities_by_filter):
        if self.player_obj:
            old_pos = self.player_obj._root.get_pos()

        self.traverser.traverse(base.render)

        if self.player_obj:
            pos = self.player_obj.position
            new_pos = self.player_obj._root.get_pos()
            z_delta = new_pos[2] - old_pos[2]
            gravity = globalClock.dt * GRAVITY
            self.player_obj.position = (new_pos[0], new_pos[1], max(pos[2] + z_delta - gravity, 1.0))
