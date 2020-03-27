from wecs.core import Component, System, and_filter
from panda3d import core
from dataclasses import field

from .terrain import TerrainObject
from .animation import Character


GRAVITY = 1.0


@Component()
class Collider:
    solid: core.CollisionSolid = None
    from_mask: int = 0
    joint_from_mask: int = 0
    into_mask: int = 1
    tangible: bool = True


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
        self.handler.add_out_pattern('%fn-outof-%in')
        self.handler.add_in_pattern('%fn-into-any')
        self.handler.add_out_pattern('%fn-outof-any')
        self.handler.horizontal = False

        base.accept('player-into-any', self._enter_swarm)
        base.accept('player-outof-any', self._leave_swarm)

        base.accept('butterfly-into-any', self._enter_butterfly)
        base.accept('butterfly-outof-any', self._leave_butterfly)

        self.player_obj = None

        self.joint_colliders = []

        self._times_swarm_activated = 0

    def init_entity(self, filter, entity):
        collider = entity[Collider]
        path = entity[TerrainObject]._root

        if not collider.solid:
            #bounds = path.get_child(0).get_bounds()
            #bury = collider.bury
            #collider.solid = core.CollisionSphere(bounds.center - (0, 0, bury), bounds.radius * 0.5 + bury)
            path.get_child(0).set_collide_mask(collider.into_mask)
            return

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

        if collider.joint_from_mask and Character in entity:
            actor = entity[Character]._actor
            self.actor = actor
            root = actor.expose_joint(None, "butterfly", "root")
            self.root = root

            for joint in actor.get_joints():
                if joint.name.startswith("butterfly."):
                    np = actor.expose_joint(root.attach_new_node(joint.name), "butterfly", joint.name, localTransform=True)
                    cpath = np.attach_new_node(core.CollisionNode("butterfly"))
                    cpath.node().set_from_collide_mask(collider.joint_from_mask)
                    cpath.node().set_into_collide_mask(collider.into_mask)
                    cpath.node().add_solid(core.CollisionSphere((0, 0.4, 0.3), 0.6))
                    cpath.node().set_tag("joint", joint.name)
                    cpath.node().modify_solid(0).set_tangible(False)
                    #cpath.show()
                    self.joint_colliders.append(cpath)
                    #self.traverser.add_collider(cpath, self.handler)

    def _enter_butterfly(self, entry):
        cpath = entry.get_from_node_path()
        exposed = cpath.get_parent()
        cpath.node().modify_solid(0).set_tangible(True)
        #saved_transform = exposed.get_transform()
        self.actor.control_joint(exposed, "butterfly", cpath.node().get_tag("joint"))
        #cpath.set_transform(saved_transform)
        self.handler.add_collider(cpath, exposed)

        #cpath.show()

    def _leave_butterfly(self, entry):
        cpath = entry.get_from_node_path()
        exposed = cpath.get_parent()
        cpath.node().modify_solid(0).set_tangible(False)
        self.actor.release_joint("butterfly", cpath.node().get_tag("joint"))
        self.handler.remove_collider(cpath)

        #cpath.hide()

    def _enter_swarm(self, entry):
        if self._times_swarm_activated == 0:
            print("Activating swarm colliders")
            for cpath in self.joint_colliders:
                self.traverser.add_collider(cpath, self.handler)

        self._times_swarm_activated += 1

    def _leave_swarm(self, entry):
        self._times_swarm_activated -= 1

        if self._times_swarm_activated == 0:
            print("Deactivating swarm colliders")
            for cpath in self.joint_colliders:
                exposed = cpath.get_parent()
                cpath.node().modify_solid(0).set_tangible(False)
                self.actor.release_joint("butterfly", cpath.node().get_tag("joint"))
                self.handler.remove_collider(cpath)
                self.traverser.remove_collider(cpath)

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
