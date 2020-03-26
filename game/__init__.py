from wecs.panda3d.core import ECSShowBase
from panda3d.core import load_prc_file
from panda3d import core
import simplepbr

from random import random, choice

from .controls import Controls, PlayerController
from .terrain import Terrain, TerrainObject, TerrainSystem
from .lighting import Sun, AmbientLight, LightingSystem
from .camera import Camera, CameraSystem
from .general import Speed
from .animation import Character, AnimationPlayer
from .collision import Collider, CollisionDetectionSystem
from .audio import SfxPlayer, Music, Listener, AudioSystem


class Game(ECSShowBase):
    def __init__(self):
        main_dir = core.ExecutionEnvironment.get_environment_variable("MAIN_DIR")
        main_dir = core.Filename.from_os_specific(main_dir)
        core.load_prc_file(core.Filename(main_dir, "settings.prc"))

        ECSShowBase.__init__(self)

        mat = core.Material()
        mat.twoside = True
        mat.base_color = (0.2, 0.2, 0.2, 1)
        mat.roughness = 0

        self.terrain = self.ecs_world.create_entity(Terrain(), name="Terrain")
        self.sun = self.ecs_world.create_entity(Sun(priority=10, intensity=3, color_temperature=6000))
        self.sun2 = self.ecs_world.create_entity(Sun(priority=0, azimuth=-90, elevation=20, intensity=0.5, color_temperature=10000))
        self.player = self.ecs_world.create_entity(
            #TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 64, 1), scale=0.09),
            TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 64, 1), scale=0.2, shadeless=True, material=mat),
            Character(
                play_rate=0.5,
                state="fly",
                states={
                    "fly": {"butterfly": "forward", "morphs": "flap"},
                },
                subparts={
                    "butterfly": ["root", "butterfly.000", "butterfly.001", "butterfly.002", "butterfly.003", "butterfly.004", "butterfly.005", "butterfly.006", "butterfly.007", "butterfly.008", "butterfly.009", "butterfly.010", "butterfly.011", "butterfly.012", "butterfly.013", "butterfly.014", "butterfly.015", "butterfly.016", "butterfly.017", "butterfly.018", "butterfly.019", "butterfly.020", "butterfly.021", "butterfly.022", "butterfly.023", "butterfly.024", "butterfly.025", "butterfly.026", "butterfly.027", "butterfly.028", "butterfly.029", "butterfly.030", "butterfly.031", "butterfly.032", "butterfly.033", "butterfly.034", "butterfly.035", "butterfly.036", "butterfly.037", "butterfly.038", "butterfly.039", "butterfly.040", "butterfly.041", "butterfly.042", "butterfly.043", "butterfly.044", "butterfly.045", "butterfly.046", "butterfly.047", "butterfly.048", "butterfly.049", "butterfly.050", "butterfly.051", "butterfly.052", "butterfly.053", "butterfly.054", "butterfly.055", "butterfly.056", "butterfly.057", "butterfly.058", "butterfly.059", "butterfly.060", "butterfly.061", "butterfly.062", "butterfly.063"],
                    "morphs": ["Key 1", "Key 2", "Key 3", "Key 4", "Key 5", "Key 6", "Key 7", "Key 8"],
                },
            ),
            Controls(acceleration=2.0),
            Speed(min=3.0, max=6.0),
            Collider(solid=core.CollisionSphere((0, 0, 0), 1.0), from_mask=1, into_mask=0),
            name="player",
        )

        camera = self.ecs_world.create_entity(
            Camera(target=self.player),
            Listener(),
            name="camera",
        )

        mat = core.Material()
        mat.twoside = True
        mat.roughness = 1
        mat.base_color = (1, 1, 1, 1)

        self.flowers = []
        for pos in [
            (128.24077881498945, 72.77485431180376, 0),
            (132.32008294369948, 80.04317696001722, 0),
            #(133.4009193432467, 79.83727034306206, 0),
            (138.97300808378307, 83.48684150117761, 0),
            #(145.89853302506023, 86.95707780906609, 0),
            (149.16924933624284, 93.18188292973764, 0),
            #(150.0381232901063, 91.2378202069885, 0),
            #(151.64899737599134, 97.48784982878404, 0),
            (150.03599905444173, 104.24586880067328, 0),
            #(146.76541251927688, 109.26866765636274, 0),
            (141.92663334350647, 114.0527358251485, 0),
            #(138.0546674357987, 120.01713618007396, 0),
            (137.43444515430608, 126.13130609854254, 0),
            #(139.27571895998688, 132.99633636935727, 0),
            (143.52169508528715, 138.78468462166003, 0),
            #(148.73723546177817, 142.71347034058024, 0),
            (155.46392914504787, 146.3215586709661, 0),
            #(161.19854639608613, 148.76522856414377, 0),
            (167.95230362806765, 149.65691705621924, 0),
            #(174.8956392426905, 147.34021636467332, 0),
            (180.4638821990831, 141.78063329568153, 0),
            #(183.54504965305318, 135.17796679895395, 0),
            (185.1086409590219, 128.92359600898587, 0),
            #(185.88186453483573, 122.74109480644104, 0),
            (187.49091467183828, 115.80290034083976, 0),
            #(190.00928424087985, 110.05787248633183, 0),
            (192.90475252264096, 104.34093522818362, 0),
            #(196.43646486107863, 98.80226570669744, 0),
            (200.35085821316372, 92.8568112843837, 0),
            #(202.3025868332382, 86.15294531813072, 0),
            (200.54392348488892, 78.95528965692367, 0),
            #(195.53559988417797, 74.65488784784873, 0),
            (189.8881664928147, 72.7373621513797, 0),
            #(183.5152002073849, 69.16919563141558, 0),
            (178.23871176836195, 63.733684609286065, 0),
            #(173.64252913896135, 56.88738322396486, 0),
            (168.91910754972935, 52.06427141526403, 0),
            #(162.1546191660268, 48.20588629414677, 0),
            (154.1682546093517, 46.49877184012427, 0),


            # Ring
            (224.25324068648297, 147.9524436758256, 0),
            (224.74846935937805, 144.1994349074313, 0),
            (226.02997098165073, 139.62188542012845, 0),
            (228.18526695794196, 136.89766430060075, 0),
            (231.28666027454278, 135.22954291835057, 0),
            (234.8748116077093, 134.9775092908075, 0),
            (238.21323153334666, 136.2878374259144, 0),
            (240.3925758087457, 138.62419160387685, 0),
            (241.42026634187215, 142.49463653061184, 0),
            (240.62472305622435, 146.1531031333106, 0),
            (238.36847157752044, 149.70438600794074, 0),
            (235.14486071395635, 151.91685016815046, 0),
            (231.1394656805694, 152.65415495009626, 0),
            (227.01753644437755, 151.5663151505824, 0),

            # Connection path
            (240.86699107197063, 125.82443995874955, 0),
            (241.29491671615156, 113.96245240498043, 0),
            (241.16597028566738, 108.45314032105024, 0),
            (240.11180577525508, 102.39336690523075, 0),
            (237.87211696591172, 97.34319370981748, 0),
            (234.33422190572497, 92.52596271515502, 0),
            (225.18437917898285, 86.50554445427109, 0),

            (144.40541250063532, 35.422677889928536, 0),
            (142.53576810882134, 29.225344858336957, 0),
            (138.8383229410278, 23.635697266638296, 0),
            (134.11276628992894, 19.024569743949158, 0),
            (128.7855626387505, 15.990961152144838, 0),
            (123.13528183681751, 14.747388049120119, 0),
            (117.34601449001879, 17.177702219031023, 0),
            (115.3575744144685, 23.178636274155057, 0),
            (145.5476220423136, 43.97049146590003, 0),
        ]:
            flower = self.ecs_world.create_entity(
                TerrainObject(self.terrain, model='models/flower.bam', position=pos, direction=random()*360, scale=0.5, material=mat),
                Character(
                    state="closed",
                    states={
                        "locked": {"flower": "closed_idle"},
                        "closed": {"flower": "closed_idle"},
                        "open": {"flower": "open_idle"},
                    },
                    transitions={
                        (None, "closed"): {"vine": "vine"},
                        ("locked", "open"): {"flower": "open", "vine": "vine"},
                        ("closed", "open"): {"flower": "open"},
                    },
                    subparts={
                        "flower": ["petal", "petal.001", "petal.002", "petal.003", "petal.004", "petal.005", "petal.006", "petal.007"],
                        "vine": ["vine"],
                    },
                ),
                SfxPlayer(sounds=['flower-open-a', 'flower-open-b', 'thorns'], volume=1000),
                Collider(solid=core.CollisionSphere((0, 0, 1.25), 1)),
                name="flower",
            )
            self.flowers.append(flower)

        self.rocks = []
        for pos in [
            (179.75304215854243, 149.04975430815733, 0),
            (180.93273624802038, 150.24433709387412, 0),
            (178.29043263410358, 158.34346624513768, 0),
            (177.6256832438217, 159.30518126483173, 0),
            (134.3215914171175, 173.988652351578, 0),
            (133.30302347421252, 174.64165330846927, 0),
            (80.94144112248188, 191.93282441406913, 0),
            (77.20476468809473, 194.00487365548406, 0),
            (79.57873359185078, 130.15171515500876, 0),
            (80.73863022680965, 126.839283605625, 0),
            (80.88561502641723, 124.01427131421939, 0),
            (79.79887931974496, 69.48015211000896, 0),
            (149.63835358731924, 33.8311999428527, 0),
            (150.18732678110973, 32.502881064685326, 0),
            (158.15873024290195, 27.68981896657041, 0),
            (179.8089155563131, 79.04630674494886, 0),
            (224.41306290164056, 88.3782599620616, 0),
            (226.2407723765043, 90.9309224570788, 0),
            (237.0522376142232, 136.17456140019024, 0),
            (132.47247814108326, 122.27847218528836, 0),
            (152.06672484882824, 133.8405784581478, 0),
            (178.86309414515873, 155.04155835228747, 0),
            (180.53078168107396, 153.37379785519641, 0),
            (137.43537002389613, 89.95124523848395, 0),
            (148.5603756930313, 117.4550714412239, 0),
            (138.37479640212072, 105.78828222093686, 0),
            (182.3238016476745, 125.01421610660083, 0),
            (205.3607911535825, 133.28229434734854, 0),
            (163.34641171619177, 200.67520097839738, 0),
            (158.4226171487318, 201.34250868968968, 0),
            (189.14832964429186, 126.82113829517645, 0),
            (244.0424530741286, 116.5356348437022, 0),
            (237.22882578369487, 157.1559093046709, 0),
            (196.15256885114437, 71.72051480474003, 0),
            (163.51313851478395, 45.48997053881406, 0),
            (141.5132813870503, 61.53002774191786, 0),
            (120.72316910563102, 20.294243109646484, 0),
            (122.24272007683149, 21.33200783788481, 0),
            (208.70198736559144, 229.25940733032687, 0),
            (86.73497131930671, 102.13899208990811, 0),
            (53.61271092518869, 24.949344475089486, 0),
            (56.05233170943425, 0.484183767313744, 0),
        ]:
            sub = choice([
                '**/rock.000',
                '**/rock.001',
                '**/rock.002',
                '**/rock.003',
                '**/rock.004',
                '**/rock.005',
                '**/rock.006',
            ])
            rock = self.ecs_world.create_entity(
                TerrainObject(self.terrain, model='models/rocks.bam', path=sub, scale=random()*2+2, position=pos, direction=random()*360, material=mat),
            )
            self.rocks.append(rock)

        tree_positions = [
            (141.44997331973642, 90.01814911779846, 0),
            (140.939259035704, 104.62580330682461, 0),
            (145.43459463675472, 120.0549962850645, 0),
            (174.96956247302137, 152.8717330910715, 0),
            (190.145361010965, 181.457325047707, 0),
            (201.05797662398624, 185.63245228897478, 0),
            (210.82617761726922, 183.22408375244615, 0),
            (232.11213740634656, 145.0250765825596, 0),
            (168.49540300577198, 43.917871248449586, 0),
            (148.15340704194222, 40.82486758175469, 0),
            (180.8336831977601, 72.20419613504203, 0),
            (186.68997325028943, 78.32692096719747, 0),
            (195.39788697159972, 81.90468045730204, 0),
            (213.25849217928504, 53.10199070005116, 0),
            (114.66943149608485, 15.391007594793304, 0),
            (52.98666565712674, 23.21233977848427, 0),
            (75.4807246783207, 58.36780909880394, 0),
            (36.67038516706891, 78.0532194542566, 0),
            (80.52830178248198, 89.48209477996595, 0),
            (80.69478875859468, 107.38463114589469, 0),
            (71.49999731337809, 152.53717564605435, 0),
            (113.74923390426176, 171.87223098072752, 0),
            (155.88697741926651, 203.82782631618855, 0),
            (160.8053323613594, 204.3887265874588, 0),
            (167.13062975700038, 209.98871913338877, 0),
            (116.12119500751355, 159.71674422503244, 0),
            (121.89508999517197, 171.6454485532199, 0),
            (125.33541961548639, 180.55647815406377, 0),
            (225.44289989186166, 94.26375479526874, 0),
            (242.03323714737428, 92.30854507678191, 0),
            (226.78261885364577, 46.699038760172556, 0),
            (236.31441122722777, 35.811792309990395, 0),
            (244.0675453062362, 41.461836300440766, 0),
            (251.88694392730682, 43.61265902663462, 0),
            (0.9360229815382952, 118.35309110859266, 0),
            (2.9367472705065185, 110.5310509314511, 0),
            (80.51599951596246, 97.06288773442499, 0),
            (3.984805460625611, 139.2271346715085, 0),
            (250.4588108563478, 140.61375465097203, 0),
            (28.25598332004428, 168.6564255412971, 0),
            (33.05219488106874, 176.59245635008432, 0),
            (39.33471815426912, 181.00305492759665, 0),
            (45.57911836533825, 188.0264031340052, 0),
            (49.84149714167223, 201.87253094669632, 0),
            (20.992753249862538, 228.1386104651079, 0),
            (14.683335768444953, 235.34901263819225, 0),
            (12.231489481186854, 241.9423527111655, 0),
            (11.8621285444361, 250.52279820373835, 0),
            (108.12901491632508, 21.768645663016716, 0),
            (120.74501892422101, 9.173819912513748, 0),

            (130.93986109342399, 245.03627995327133, 0),
            (123.47617711611365, 236.5177887693719, 0),
            (118.54018894903761, 230.31552873125054, 0),
            (112.11442258649323, 229.15232753210634, 0),
            (115.33554257802335, 235.12176260428103, 0),
            (188.00154226065294, 244.918254643617, 0),
        ]
        tree_scales = [random()*0.5+0.5 for pos in tree_positions]
        tree_directions = [random()*360 for dir in tree_positions]

        # Hack to wrap around map
        for pos, scale, dir in list(zip(tree_positions, tree_scales, tree_directions)):
            if pos[0] < 64:
                tree_positions.append((pos[0] + 256, pos[1], 0))
                tree_scales.append(scale)
                tree_directions.append(dir)
            if pos[1] < 64:
                tree_positions.append((pos[0], pos[1] + 256, 0))
                tree_scales.append(scale)
                tree_directions.append(dir)

            if pos[0] > 256 - 64:
                tree_positions.append((pos[0] - 256, pos[1], 0))
                tree_scales.append(scale)
                tree_directions.append(dir)
            if pos[1] > 256 - 64:
                tree_positions.append((pos[0], pos[1] - 256, 0))
                tree_scales.append(scale)
                tree_directions.append(dir)

        tree_shader = core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/tree.vert", "assets/shaders/object.frag")

        self.trees = []
        for pos, scale, dir in zip(tree_positions, tree_scales, tree_directions):
            sub = choice([
                '**/tree',
                '**/tree.001',
                '**/tree.002',
                '**/tree.003',
            ])
            #pos = (pos[0], pos[1], -random())
            tree = self.ecs_world.create_entity(
                TerrainObject(self.terrain, model='models/trees.bam', path=sub, scale=scale, position=pos, direction=dir, material=mat, shader=tree_shader),
                name="tree",
            )
            self.trees.append(tree)

        #self.ecs_world.create_entity(AmbientLight(intensity=0.1, color=(0.5, 0.7, 0.5)))

        self.music = self.ecs_world.create_entity(Music(songs=["peace", "chase"], current="peace"), name="music")
        self.ambient = self.ecs_world.create_entity(SfxPlayer(sounds=['background'], loop=True))
        self.ambient[SfxPlayer].play('background')

        self.add_system(PlayerController(), sort=-1)
        self.add_system(TerrainSystem(), sort=0)
        self.add_system(LightingSystem(), sort=1)
        self.add_system(CameraSystem(), sort=2)
        self.add_system(AnimationPlayer(), sort=3)
        self.add_system(CollisionDetectionSystem(), sort=4)
        self.add_system(AudioSystem(), sort=5)

        self.disable_mouse()
        simplepbr.init(msaa_samples=0, max_lights=2)

        self.accept('f12', self.screenshot)
        self.accept('1', self.oobeCull)
        self.accept('p', self.print_pos)

        self.accept('player-into-flower', self.handle_collision)

        self.render.find("**/butterfly").set_color((2.0, 0.5, 1.0, 1), 10000)
        self.render.find("**/butterfly").set_color_scale((1, 1, 1, 1), 10000)
        self.render.find("**/butterfly").set_shader_off(20)

        sky = loader.load_model("models/sky")
        sky.set_bin('background', 1)
        sky.set_depth_write(False)
        sky.set_depth_test(False)
        sky.reparent_to(base.cam)
        sky.set_compass()
        sky.set_scale(3)
        sky.set_shader_off(10)
        sky.set_light_off(10)
        sky.set_color_scale((0.7, 0.8, 1.0, 1.0))

        self.num_flowers = 0

        self.render.set_shader(core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/object.vert", "assets/shaders/object.frag"), 10)

        #print(self.camList)

    def print_pos(self):
        pos = self.player[TerrainObject].position
        print('                ' + str((pos[0], pos[1], 0)) + ',')

    def handle_collision(self, entry):
        flower = entry.into_node.get_python_tag('entity')
        if flower[Character].state == 'open':
            return

        flower[Character].state = 'open'
        flower[SfxPlayer].play(choice(['flower-open-a', 'flower-open-b']))

        #self.player[Speed].current = 0.0
        #self.player[Controls].enabled = False

        #self.player[TerrainObject]._root.hprInterval(4, (360, 0, 0), blendType='easeInOut').start()

        self.num_flowers += 1


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
