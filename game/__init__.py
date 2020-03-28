from wecs.panda3d.core import ECSShowBase
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from panda3d.core import load_prc_file
from panda3d import core
import simplepbr

from random import random, choice
import math

from .controls import Controls, PlayerController
from .terrain import Terrain, TerrainObject, TerrainSystem
from .lighting import Sun, AmbientLight, LightingSystem
from .camera import Camera, CameraSystem
from .general import Speed
from .animation import Character, AnimationPlayer
from .collision import Collider, GeomCollider, CollisionDetectionSystem
from .audio import SfxPlayer, Music, Listener, AudioSystem


PAINT_THRESHOLD = 0.78


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
        self.sun = self.ecs_world.create_entity(Sun(priority=10, intensity=3, color_temperature=7000))
        self.sun2 = self.ecs_world.create_entity(Sun(priority=0, azimuth=-90, elevation=20, intensity=0.5, color_temperature=10000))
        self.player = self.ecs_world.create_entity(
            #TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 64, 1), scale=0.09),
            TerrainObject(self.terrain, model='models/butterfly.bam', position=(128, 60, 1), scale=0.2, shadeless=True, material=mat),
            Character(
                state="fly",
                states={
                    "fly": {"butterfly": "forward", "morphs": "flap"},
                    "end": {"morphs": "flap"},
                },
                play_rates={
                    "fly": 0.5,
                    "end": 1.0,
                },
                transitions={
                    ("fly", "end"): {"butterfly": "dance"},
                },
                subparts={
                    "butterfly": ["root", "butterfly.000", "butterfly.001", "butterfly.002", "butterfly.003", "butterfly.004", "butterfly.005", "butterfly.006", "butterfly.007", "butterfly.008", "butterfly.009", "butterfly.010", "butterfly.011", "butterfly.012", "butterfly.013", "butterfly.014", "butterfly.015", "butterfly.016", "butterfly.017", "butterfly.018", "butterfly.019", "butterfly.020", "butterfly.021", "butterfly.022", "butterfly.023", "butterfly.024", "butterfly.025", "butterfly.026", "butterfly.027", "butterfly.028", "butterfly.029", "butterfly.030", "butterfly.031", "butterfly.032", "butterfly.033", "butterfly.034", "butterfly.035", "butterfly.036", "butterfly.037", "butterfly.038", "butterfly.039", "butterfly.040", "butterfly.041", "butterfly.042", "butterfly.043", "butterfly.044", "butterfly.045", "butterfly.046", "butterfly.047", "butterfly.048", "butterfly.049", "butterfly.050", "butterfly.051", "butterfly.052", "butterfly.053", "butterfly.054", "butterfly.055", "butterfly.056", "butterfly.057", "butterfly.058", "butterfly.059", "butterfly.060", "butterfly.061", "butterfly.062", "butterfly.063"],
                    "morphs": ["Key 1", "Key 2", "Key 3", "Key 4", "Key 5", "Key 6", "Key 7", "Key 8"],
                },
            ),
            Controls(acceleration=2.0),
            Speed(min=3.0, max=6.0),
            Collider(solid=core.CollisionSphere((0, 0.5, 0), 2), from_mask=0b01, joint_from_mask=0b10, into_mask=0, tangible=False),
            name="player",
        )

        camera = self.ecs_world.create_entity(
            Camera(target=self.player),
            Collider(solid=core.CollisionSphere((0, 0, 0), 3), from_mask=0b10, tangible=False),
            Listener(),
            name="camera",
        )

        mat = core.Material()
        mat.twoside = True
        mat.roughness = 1
        mat.base_color = (1, 1, 1, 1)

        self.dolmen = self.ecs_world.create_entity(
            TerrainObject(
                self.terrain,
                model='models/hunebed.bam',
                scale=1,
                position=(164.38, 238.85, 0),
                direction=0,
                material=mat,
                wraparound=100,
            ),
            Collider(into_mask=0b01, tangible=False),
            GeomCollider(into_mask=0b10),
            name="dolmen",
        )

        self.superflower = self.ecs_world.create_entity(
            TerrainObject(
                self.terrain,
                model='models/superflower.bam',
                position=(160.6078540733596, 234.90864229056726, 0),
                #position=(120.64369917139119, 83.10867386895148, 0),
                scale=0.75,
                material=mat,
            ),
            Character(
                state="locked",
                states={
                    "locked": {"flower": "closed_idle"},
                    "closed": {"flower": "closed_idle"},
                    "open": {"flower": ""},
                },
                transitions={
                    ("locked", "closed"): {"vine": "vine"},
                    ("locked", "open"): {"flower": "open", "vine": "vine"},
                    ("closed", "open"): {"flower": "open"},
                },
                subparts={
                    "flower": ["petal", "petal.001", "petal.002", "petal.003", "petal.004", "petal.005", "petal.006", "petal.007"],
                    "vine": ["vine"],
                },
                play_rates={
                    "locked": 2.5,
                    "closed": 2.5,
                    "open": 2.5,
                },
            ),
            SfxPlayer(sounds=['flower-open-a', 'flower-open-b', 'flower-open-c', 'dance'], volume=1),
            Collider(solid=core.CollisionTube((0, 0, 0), (0, 0, 3), 0.5), into_mask=0b11, tangible=True),
            name="superflower",
        )

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
            #(238.21323153334666, 136.2878374259144, 0),
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
            #(225.18437917898285, 86.50554445427109, 0),
            (214.0419069842869, 82.20714784400558, 0),
            (227.0915502805343, 83.31047993039502, 0),

            (144.40541250063532, 35.422677889928536, 0),
            #(142.53576810882134, 29.225344858336957, 0),
            (138.8383229410278, 23.635697266638296, 0),
            #(134.11276628992894, 19.024569743949158, 0),
            (128.7855626387505, 15.990961152144838, 0),
            #(123.13528183681751, 14.747388049120119, 0),
            (117.34601449001879, 17.177702219031023, 0),
            #(115.3575744144685, 23.178636274155057, 0),
            (145.5476220423136, 43.97049146590003, 0),

            # Another ring
            (108.19437718515435, 24.58976171768642, 0),
            #(101.31484050741551, 25.567191720598508, 0),
            (95.26477256154789, 28.050311831704228, 0),
            #(89.44097511047566, 32.106964269374195, 0),
            (84.11303008752341, 37.804850080198456, 0),
            #(80.20422271747601, 43.81329931232724, 0),
            (77.3130242761945, 51.484231578003715, 0),
            (79.75548777142643, 55.40912507443539, 0),
            (81.85357174767407, 59.273140495690384, 0),
            (78.12489121500599, 63.32190377160861, 0),
            (71.98775315369242, 61.611005612352926, 0),
            (70.13420211243033, 56.38959284874809, 0),
            (75.31712540816625, 52.40333503562683, 0),
            (76.08579656459118, 70.39394585510323, 0),
            (76.83312450826354, 81.81511986798962, 0),
            (77.53064238332415, 92.22656953703483, 0),
            (76.97514029795386, 99.77443737162557, 0),
            (77.10428934020467, 108.46659600799124, 0),

            (79.27446828297043, 135.62930646908575, 0),
            (86.82430599042767, 142.9109391314034, 0),
            (97.21348719858959, 151.34973196779322, 0),
            (98.78740261374203, 164.7445577144036, 0),
            (100.83834890367783, 178.6139922863031, 0),
            (102.87866006380524, 192.40579236670126, 0),
            (104.320626460479, 205.22144514121095, 0),
            (106.87500959760752, 237.038629505919, 0),
            (102.20281233432881, 222.18309831240288, 0),

            (57.72114627705365, 23.13809485169263, 0),
            (54.83568570922412, 14.708424929273024, 0),
            (54.27767980201529, 5.3782874419989755, 0),
            (53.272139304689944, 252.46196150562707, 0),
            (51.01050041599985, 243.83820524954257, 0),
            (48.80560174800455, 241.33605087004472, 0),
            (39.329678836652214, 236.1429311063105, 0),
            (31.14546466199422, 230.70760410053472, 0),
            (21.611261251579762, 223.60075249286575, 0),
            (11.843669443919978, 217.0793381945025, 0),
            (5.536457891524848, 208.61876431656694, 0),
            (255.09809425539206, 195.8263185678207, 0),
            (251.39547612381514, 184.7141102190906, 0),
            (248.58198579152662, 171.77483939009534, 0),
            (246.53870804720572, 161.98961466808638, 0),
            (243.8368990519704, 151.31974655348137, 0),


            #(149.2144335705672, 14.578011501734217, 0),
            #(156.94364947478599, 9.58994436478866, 0),
            #(164.03014099142175, 6.00799063985961, 0),
            #(171.07765062675256, 3.334500417197855, 0),
            #(179.2444548665613, 1.1123368945131376, 0),
            #(215.27848986739903, 1.031311104213051, 0),
            #(222.01174636794326, 3.670624741845923, 0),
            (229.94915633552202, 8.25574379953187, 0),
            (236.18989881642997, 14.191817719770912, 0),
            (241.20794871012063, 22.411911443845636, 0),
            (243.55571339998644, 30.353414815761774, 0),
            (243.56905632042873, 37.76905228541563, 0),
            (240.58237847884453, 43.96967140496043, 0),
            (232.72858330553848, 48.48786286723826, 0),
            (224.81109773500796, 47.861669040492494, 0),
            (221.03124861041616, 41.109409619364044, 0),
            (226.95840539191792, 35.410150756790976, 0),

            # A trio

            (89.90026699678978, 113.69701450486184, 0),
            (96.54471054383173, 102.66577856382757, 0),
            (90.30983739216052, 95.53393310320703, 0),

            (136.37815410409448, 184.2896357815367, 0),
            (185.55730135432339, 189.91360389837496, 0),
            (204.09846544959535, 188.7803899075964, 0),
            (215.90876652182146, 198.16845079019424, 0),
            (221.4337231710032, 212.24022789691972, 0),
            (216.93893100503382, 228.37042317059561, 0),

            (29.350722419175685, 241.3910478606554, 0),
            (20.133346821568303, 249.61823994600195, 0),
            (10.346773845022398, 248.06873447397248, 0),
            (8.687520306138117, 234.0175857929473, 0),
            (180.19359198916518, 167.46072283728094, 0),

            (153.53915644535368, 27.754359273640638, 0),
            (161.38353718142577, 29.757919414068702, 0),
            (170.0677590490259, 30.130271092380312, 0),
            (179.59339329972286, 28.597703363452794, 0),
            (189.4279392765973, 28.067489001699336, 0),
            (198.33499750013354, 29.65868343871907, 0),
            (207.16257103300913, 33.525396320724234, 0),
            (214.26991964342764, 37.89603016703796, 0),

            # Slalom

            (243.01162964101823, 53.29815236126152, 0),
            (251.60862542062415, 60.85632002783746, 0),
            (2.735007844058824, 69.53734218273168, 0),
            (14.095482024606563, 77.69082801005295, 0),
            (23.471972039490677, 81.91639930162111, 0),
            (32.30166252501987, 87.55152763025269, 0),
            (37.65790702312686, 94.66520162513443, 0),
            (39.7626447039763, 105.40147597228956, 0),
            (36.69907274701938, 115.07697813648598, 0),
            (30.113742242883983, 124.51823041776727, 0),
            (24.911534200174604, 135.1609474815683, 0),
            (28.147477481464907, 145.84393781692188, 0),
            (36.43823838904034, 150.21278243608475, 0),
            (45.96640551063055, 147.5180452017424, 0),
            (51.980574624105074, 148.36291831180316, 0),
            (59.795262439512925, 153.2373224274378, 0),
            (63.95897676752707, 161.86351987200433, 0),
            (63.097615671776516, 172.58966025813183, 0),
            (61.538210896745355, 182.6335184444167, 0),
            (64.86929596875241, 192.97914576198494, 0),
            (74.59525860771423, 197.6119924807432, 0),
            (87.00369706327608, 194.2260882310563, 0),
            (103.1733320858391, 250.00764526828317, 0),
            (94.15939093923622, 255.62837785668094, 0),
            #(83.67401654337496, 2.7149590232081624, 0),
            #(70.60850191243787, 1.789399027573447, 0),
            (59.59424926217645, 253.8583515280184, 0),

            (48.25640806258084, 31.462588487650162, 0),
            (37.25979121729276, 35.13604875662652, 0),
            (28.273100212972505, 40.58901664369962, 0),
            (24.242033957115755, 52.87812053035312, 0),
            (24.42399217723482, 67.60412822483853, 0),


            (23.11302685143048, 177.24147101040091, 0),
            (29.917117500964366, 186.47212327273195, 0),
            (36.97620642816884, 195.17909739273503, 0),
            (43.31169944703755, 204.43899210882407, 0),
            (47.94207758981136, 216.11495863692357, 0),
            (46.6431495617351, 229.2515768394893, 0),

            (79.07814213913232, 116.05322856954518, 0),
            (77.9722924574722, 123.58716911561608, 0),
            (76.53528353884747, 132.9635164541018, 0),

            (79.70955065957168, 255.9534151970939, 0),

            (113.38319537719572, 173.90327438610638, 0),
            (147.372899053233, 186.2782833936401, 0),
            (159.38698064080037, 185.01081456322132, 0),
            (169.96448788947714, 185.0386365677651, 0),
            (219.89807924012396, 236.9262004051333, 0),
            (225.55292310898577, 248.69549737791857, 0),

            (109.92257598784407, 152.99223398636448, 0),
            (122.41572428622283, 144.0090112324044, 0),

            (70.01113153984998, 35.50622703985409, 0),
        ]:
            flower = self.ecs_world.create_entity(
                TerrainObject(
                    self.terrain,
                    model='models/flower.bam',
                    position=pos,
                    direction=random()*360,
                    scale=0.5,
                    material=mat,
                    wraparound=64,
                ),
                Character(
                    state="closed",
                    states={
                        "locked": {"flower": "closed_idle"},
                        "closed": {"flower": "closed_idle"},
                        "open": {"flower": ""},
                    },
                    transitions={
                        #(None, "closed"): {"vine": "vine"},
                        ("locked", "open"): {"flower": "open", "vine": "vine"},
                        ("closed", "open"): {"flower": "open"},
                    },
                    subparts={
                        "flower": ["petal", "petal.001", "petal.002", "petal.003", "petal.004", "petal.005", "petal.006", "petal.007"],
                        "vine": ["vine"],
                    },
                    play_rates={
                        "locked": 2.5,
                        "closed": 2.5,
                        "open": 2.5,
                    },
                ),
                SfxPlayer(sounds=['flower-open-a', 'flower-open-b', 'flower-open-c'], volume=1),
                Collider(solid=core.CollisionSphere((0, 0, 1.25), 0.2), into_mask=0b01, tangible=False),
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
            (235.80029146524143, 41.958280144946315, 0),
            (40.27292605760751, 79.57967833095057, 0),
            (18.709533272278772, 241.59275210676637, 0),
            (144.31505779068812, 250.57853808283957, 0),
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
                TerrainObject(
                    self.terrain,
                    model='models/rocks.bam',
                    path=sub,
                    scale=random()*2+3,
                    position=pos,
                    direction=random()*360,
                    material=mat,
                    wraparound=100,
                ),
                Collider(into_mask=0b01, tangible=False),
                GeomCollider(into_mask=0b10),
                name="rock",
            )
            self.rocks.append(rock)

        tree_shader = core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/tree.vert", "assets/shaders/object.frag")

        shrub_positions = [
            (145.1654531609378, 84.56205859354166, 0),
            (133.99739124052564, 95.74738159686336, 0),
            (188.5086361801647, 81.75343430304068, 0),
            (120.84985539195297, 25.173721786609676, 0),
            (113.72210369152982, 86.11736839885505, 0),
            (118.45254222807526, 130.11084531968396, 0),
            (105.90369980618854, 62.35300278787522, 0),
            (132.81316677395853, 54.375810660374704, 0),
            (159.66544847341189, 75.52744392827569, 0),
            (166.1590325302975, 120.11470288184765, 0),
            (200.25444817153718, 151.5906149350707, 0),
            (213.10247047346476, 156.3558456952619, 0),
            (233.2862580111869, 171.50089134617275, 0),
            (249.92281566048962, 177.27985320523442, 0),
            (3.9003201741741074, 169.4261505038755, 0),
            (12.707674765333122, 128.76098271730848, 0),
            (12.646384986309279, 95.51199824924912, 0),
            (10.050388457165626, 91.02504625192826, 0),
            (5.892282737657839, 79.47690069742129, 0),
            (15.188800587787489, 58.6806465252775, 0),
            (20.264281891824584, 43.15770845437191, 0),
            (11.565858020142342, 31.969478989863532, 0),
            (9.226745131047528, 30.45448498551221, 0),
            (243.60031874826592, 5.971163450485722, 0),
            (240.80898729102034, 0.9199952083555893, 0),
            (236.93673779892953, 209.96322605886854, 0),
            (230.20474611141256, 179.84192001708206, 0),
            (107.51525220879986, 254.1160487773983, 0),
            (82.67618586737444, 240.58257896138812, 0),
            (79.89228747973159, 236.22924514278054, 0),
            (57.787041859678276, 230.07526546529877, 0),
            (41.065727410696546, 216.72682489633542, 0),
            (36.459922155495775, 204.9283085806328, 0),
            (53.23451081174334, 165.643973419102, 0),
            (39.13047237358696, 144.00193382852962, 0),
            (43.450422436725525, 114.2936127733581, 0),
            (38.40750632176204, 108.82287304161925, 0),
            (223.65100226296684, 111.22770794568294, 0),
            (208.2963932548011, 108.06589481179485, 0),
            (183.41914894051658, 103.59768071774427, 0),
            (248.79661291648947, 70.35523492614341, 0),
            (198.17874225438027, 121.72120637025128, 0),
            (175.51503316879152, 174.29220958021978, 0),
            (164.40558435819503, 173.09115365242212, 0),
            (134.67220837947667, 161.44469876496265, 0),
            (89.51731449354446, 168.58697374325217, 0),
            (71.12139972322547, 182.84411836889686, 0),
            (28.24641123311496, 214.30461995647966, 0),
            (243.95284739415047, 237.09047824903968, 0),
            (229.65242057585226, 240.47426114245573, 0),
            (217.05179232392942, 21.28722249456183, 0),
            (18.926434323735435, 108.06204409748898, 0),
            (70.37356286571604, 123.7372719120398, 0),
            (92.16250483615904, 143.28778753990068, 0),
            (144.7786389609179, 121.91396692159228, 0),
            (196.95297022878256, 198.07484091148734, 0),
            (193.13275512203094, 16.591565950078163, 0),
            (188.25510033641814, 50.06646394365584, 0),
            (197.5745381255224, 46.908633370961695, 0),
            (218.05442077615604, 27.88806244037831, 0),
            (155.33119764893593, 187.22615080867038, 0),
            (83.3053123099234, 31.260258049062095, 0),
            (58.022967222165775, 70.75000957914604, 0),
            (129.76709802126658, 205.23256930110296, 0),
            (109.87584066549704, 196.23776666594298, 0),
            (69.66903092290568, 2.340512632039162, 0),
            (82.49145313340462, 28.238068870234255, 0),
        ]
        self.shrubs = []
        for pos in shrub_positions:
            scale = random()*0.125+0.45
            dir = random()*360
            sub = choice([
                '**/shrub',
                '**/shrub.001',
                '**/shrub.002',
                '**/shrub.003',
            ])
            shrub = self.ecs_world.create_entity(
                TerrainObject(
                    self.terrain,
                    model='models/shrub.bam',
                    path=sub,
                    scale=scale,
                    position=pos,
                    direction=dir,
                    material=mat,
                    shader=tree_shader,
                    wraparound=64,
                    draw_distance=64,
                ),
                Collider(solid=core.CollisionSphere((0, 0, 1), 1.3), into_mask=0b11),
                name="shrub",
            )
            self.shrubs.append(shrub)

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
            #(188.00154226065294, 244.918254643617, 0),
        ]

        self.trees = []
        for pos in tree_positions:
            scale = random()*0.5+0.5
            dir = random()*360
            sub = choice([
                '**/tree',
                '**/tree.001',
                '**/tree.002',
                '**/tree.003',
            ])
            #pos = (pos[0], pos[1], -random())
            tree = self.ecs_world.create_entity(
                TerrainObject(
                    self.terrain,
                    model='models/trees.bam',
                    path=sub,
                    scale=scale,
                    position=pos,
                    direction=dir,
                    material=mat,
                    shader=tree_shader,
                    wraparound=120,
                ),
                Collider(solid=core.CollisionCapsule((0, 0, -1), (0, 0, 5), 0.5), into_mask=0b11),
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
        self.accept('2', self.press_2)
        self.accept('3', self.press_3)
        self.accept('4', self.ending)
        self.accept('p', self.print_pos)

        self.accept('player-into-flower', self.handle_collision)

        #self.render.find("**/butterfly").set_color((2.0, 0.5, 1.0, 1), 10000)
        #self.render.find("**/butterfly").set_color_scale((1, 1, 1, 1), 10000)
        #self.render.find("**/butterfly").set_shader_off(20)

        sky = loader.load_model("models/sky")
        sky.set_bin('background', 1)
        sky.set_depth_write(False)
        sky.set_depth_test(False)
        sky.reparent_to(base.cam)
        sky.set_compass()
        sky.set_scale(5)
        sky.set_shader_off(10)
        sky.set_light_off(10)
        sky.set_color_scale((0.7, 0.8, 1.0, 1.0))

        self.num_flowers = len(self.flowers)

        self.render.set_shader(core.Shader.load(core.Shader.SL_GLSL, "assets/shaders/object.vert", "assets/shaders/object.frag"), 10)

        #print(self.camList)

        radius = 12
        size = math.ceil(radius * 2)
        half_size = size * 0.5
        r = half_size / radius
        self.spot = core.PNMImage(size, size, 2)
        self.spot.render_spot((1, 1, 1, 1), (1, 1, 1, 0), 0, r)
        self.spot.apply_exponent(2, 2, 2, 2)

        self._last_note = 'flower-open-c'

        cm = core.CardMaker("minimap")
        cm.set_frame(-1, 0, 0, 1)
        cm.set_uv_range((0, 0), (1, 1))
        self.minimap = base.a2dBottomRight.attach_new_node(cm.generate())
        self.minimap.set_texture(self.terrain[Terrain]._sat_tex)
        self.minimap.set_scale(2/3.0)
        self.minimap.hide()
        self.minimap.set_transparency(1)
        self.minimap.set_alpha_scale(0.75)

        sz = 0.025
        cm = core.CardMaker("dolmen")
        cm.set_frame(-sz, sz, -sz, sz)
        cm.set_color((0.5, 0.5, 0.5, 1))

        pos = self.dolmen[TerrainObject].position
        minimap_icon = self.minimap.attach_new_node(cm.generate())
        minimap_icon.set_texture_off(10)
        minimap_icon.set_pos(pos[0] / 256 - 1, 0, pos[1] / 256)
        minimap_icon.set_r(45)

        sz = 0.005
        cm = core.CardMaker("flower")
        cm.set_frame(-sz, sz, -sz, sz)
        cm.set_color((0.9, 0.2, 0.2, 1))

        self.flower_icons = {}

        for flower in self.flowers:
            pos = flower[TerrainObject].position
            minimap_icon = self.minimap.attach_new_node(cm.generate())
            minimap_icon.set_texture_off(10)
            minimap_icon.set_pos(pos[0] / 256 - 1, 0, pos[1] / 256)
            self.flower_icons[flower._uid] = minimap_icon

        sz = 0.0075
        cm = core.CardMaker("superflower")
        cm.set_frame(-sz, sz, -sz, sz)
        cm.set_color((0.9, 1.0, 0.0, 1))

        pos = self.superflower[TerrainObject].position
        minimap_icon = self.minimap.attach_new_node(cm.generate())
        minimap_icon.set_texture_off(10)
        minimap_icon.set_pos(pos[0] / 256 - 1, 0, pos[1] / 256)
        self.flower_icons[self.superflower._uid] = minimap_icon

        sz = 0.005
        cm = core.CardMaker("tree")
        cm.set_frame(-sz, sz, -sz, sz)
        cm.set_color((0.0, 0.5, 0.0, 1))

        for tree in self.trees:
            pos = tree[TerrainObject].position
            minimap_icon = self.minimap.attach_new_node(cm.generate())
            minimap_icon.set_texture_off(10)
            minimap_icon.set_pos(pos[0] / 256 - 1, 0, pos[1] / 256)

        sz = 0.01
        cm = core.CardMaker("cursor")
        cm.set_frame(-sz, sz, -sz, sz)
        cm.set_color((0.4, 0.2, 0.7, 1))
        minimap_icon = self.minimap.attach_new_node(cm.generate())
        minimap_icon.set_texture_off(10)
        arrow = minimap_icon.attach_new_node(cm.generate())
        arrow.set_r(45)
        arrow.set_scale(0.707)
        arrow.set_z(0.01)
        self.minimap_icon = minimap_icon

        self.accept('m', self.toggle_minimap)

        self._goodenough_activated = False

        #for flower in self.flowers:
        #    self.paint_at(flower[TerrainObject].position)

        vine = self.superflower[Character]._state_actors['locked'].find('**/vine')
        vine.set_color((188/430.0, 152/430.0, 101/430.0, 1.0), 1000)

        vine = self.superflower[Character]._state_actors['closed'].find('**/vine')
        vine.remove_node()

        vine = self.superflower[Character]._state_actors['open'].find('**/vine')
        vine.remove_node()

        self.player[Character]._actor.loop('flap', partName='morphs')
        self.player[Character]._state_actors['end'].hide()

    def toggle_minimap(self):
        if not self.minimap.is_hidden():
            self.minimap.hide()
            self.taskMgr.remove('update-minimap')
            return

        self.minimap.show()
        self.taskMgr.add(self._update_minimap, 'update-minimap')

    def _update_minimap(self, task):
        pos = self.player[TerrainObject].position
        self.minimap_icon.set_pos(pos[0] / 256 - 1, 0, pos[1] / 256)
        self.minimap_icon.set_r(-self.player[TerrainObject].direction)
        return task.cont

    def print_pos(self):
        pos = self.player[TerrainObject].position
        print('            ' + str((pos[0], pos[1], 0)) + ',')

    def press_2(self):
        for flower in self.flowers:
            self.paint_at(flower[TerrainObject].position)

        terrain = self.terrain[Terrain]

    def press_3(self):
        self.enough_paint()
        terrain = self.terrain[Terrain]

    def handle_collision(self, entry):
        flower = entry.into_node.get_python_tag('entity')
        self.pollinate_flower(flower)

    def pollinate_flower(self, flower):
        if Character in flower:
            if flower[Character].state == 'open':
                return

            flower[Character].state = 'open'

        if flower._uid in self.flower_icons:
            self.flower_icons[flower._uid].remove_node()

        if Collider in flower:
            del flower[Collider]

        if flower._uid.name == 'flower':
            notes = set(['flower-open-a', 'flower-open-b', 'flower-open-c'])
            notes.discard(self._last_note)
            note = choice(list(notes))
            flower[SfxPlayer].play(note)
            self._last_note = note
        elif flower._uid.name == 'superflower':
            flower[SfxPlayer].play('flower-open-a')
            flower[SfxPlayer].play('flower-open-b')
            flower[SfxPlayer].play('flower-open-c')

        #self.player[Speed].current = 0.0
        #self.player[Controls].enabled = False

        obj = flower[TerrainObject]
        pos = obj.position

        self.paint_at(pos)

        #self.player[TerrainObject]._root.hprInterval(4, (360, 0, 0), blendType='easeInOut').start()
        if flower._uid.name == "flower":
            self.num_flowers -= 1

            if not self._goodenough_activated:
                print("%d flowers to go!" % (self.num_flowers))

        elif flower._uid.name == "superflower":
            # Superflower.
            self.ending()

    def enough_paint(self):
        if self._goodenough_activated:
            return
        self._goodenough_activated = True

        # Pollinate all remaining flowers.
        for flower in self.flowers:
            if Character in flower and flower[Character].state == 'closed':
                self.pollinate_flower(flower)

        print("Good enough!")
        dolly = self.player[TerrainObject]._root.attach_new_node("dolly")
        dolly.set_compass()
        saved_xform = base.cam.get_transform()
        saved_parent = base.cam.get_parent()
        base.cam.wrt_reparent_to(dolly)

        dolmen_pos = self.dolmen[TerrainObject]._root.get_pos()

        # Which way around is quicker?
        pos = self.player[TerrainObject].position
        if pos[1] < dolmen_pos[1] - 128:
            dolmen_pos.y -= 256

        old_hpr = base.cam.get_hpr()
        base.cam.set_pos(base.cam.get_pos() + (0, 0, 10))
        base.cam.look_at(render, dolmen_pos)
        look_hpr = base.cam.get_hpr()
        base.cam.set_hpr(old_hpr)
        base.cam.set_pos(base.cam.get_pos() - (0, 0, 10))

        while look_hpr[0] > old_hpr[0] + 180:
            look_hpr[0] -= 360
        while look_hpr[0] < old_hpr[0] - 180:
            look_hpr[0] += 360

        Sequence(
            Parallel(
                dolly.posInterval(3, (0, 0, 10), blendType='easeInOut'),
                base.cam.hprInterval(3, look_hpr, blendType='easeInOut'),
            ),
            Wait(2.0),
            Parallel(
                dolly.posInterval(1.5, (0, 0, 0), blendType='easeInOut'),
                base.cam.hprInterval(1.5, old_hpr, blendType='easeInOut'),
            ),
            Func(lambda: (base.cam.reparent_to(saved_parent) or base.cam.set_transform(saved_xform))),
        ).start()

        if Character in self.superflower:
            self.superflower[Character].state = 'closed'

        self.accept('player-into-superflower', self.handle_collision)

    def ending(self):
        self._goodenough_activated = True

        if Controls in self.player:
            del self.player[Controls]

        pos = self.superflower[TerrainObject].position
        pos = (pos[0], pos[1], 2.5)
        self.player[TerrainObject].position = pos

        pos = (pos[0], pos[1], self.superflower[TerrainObject]._root.get_z() + 2.5)
        self.player[TerrainObject]._root.set_pos(pos)

        self.player[Character].state = 'end'
        self.superflower[SfxPlayer].play('dance')
        self.player[Character]._actor.set_play_rate(0.5, 'flap', partName='morphs')

        dolly = render.attach_new_node("dolly")
        dolly.set_pos(pos[0], pos[1], pos[2] + 2.5)
        saved_xform = base.cam.get_transform()
        saved_parent = base.cam.get_parent()
        base.cam.wrt_reparent_to(dolly)

        old_hpr = base.cam.get_hpr()
        look_hpr = core.VBase3(0, -30, 0)

        while look_hpr[0] > old_hpr[0] + 180:
            look_hpr[0] -= 360
        while look_hpr[0] < old_hpr[0] - 180:
            look_hpr[0] += 360

        base.transitions.setFadeColor(1, 1, 1)
        Sequence(
            Parallel(
                Sequence(Wait(2.0), Func(self.fill_map)),
                base.cam.posInterval(3, (0, -10, 5), blendType='easeInOut'),
                base.cam.hprInterval(4, look_hpr, blendType='easeInOut'),
                dolly.scaleInterval(14, 1.5, blendType='easeInOut'),
            ),
            base.transitions.getFadeOutIval(3.0),
        ).start()

    def fill_map(self):
        terrain = self.terrain[Terrain]
        terrain._sat_img.fill(1)
        terrain._sat_tex.load(terrain._sat_img)

    def paint_at(self, pos):
        terrain = self.terrain[Terrain]
        bound = terrain._sat_img.get_x_size() - 1

        #num_steps = int(math.ceil(2.5 / globalClock.dt))
        num_steps = 80
        per_step = 0.333 / num_steps

        point = pos[0] * terrain._scale.x * bound, (bound - pos[1] * terrain._scale.y * bound)

        def paint_more(task):
            px_x = int(round(point[0] - self.spot.get_x_size() / 2))
            px_y = int(round(point[1] - self.spot.get_y_size() / 2))
            terrain._sat_img.blend_sub_image(
                self.spot,
                px_x,
                px_y,
                0, 0, -1, -1,
                (per_step * 0.1) * (task.get_elapsed_frames() + 1)
            )

            if px_x < self.spot.get_x_size():
                terrain._sat_img.blend_sub_image(
                    self.spot,
                    px_x + terrain._sat_img.get_x_size(),
                    px_y,
                    0, 0, -1, -1,
                    (per_step * 0.1) * (task.get_elapsed_frames() + 1)
                )

            if px_y < self.spot.get_y_size():
                terrain._sat_img.blend_sub_image(
                    self.spot,
                    px_x,
                    px_y + terrain._sat_img.get_y_size(),
                    0, 0, -1, -1,
                    (per_step * 0.1) * (task.get_elapsed_frames() + 1)
                )

            if px_x > terrain._sat_img.get_x_size() - self.spot.get_x_size():
                terrain._sat_img.blend_sub_image(
                    self.spot,
                    px_x - terrain._sat_img.get_x_size(),
                    px_y,
                    0, 0, -1, -1,
                    (per_step * 0.1) * (task.get_elapsed_frames() + 1)
                )

            if px_y > terrain._sat_img.get_y_size() - self.spot.get_y_size():
                terrain._sat_img.blend_sub_image(
                    self.spot,
                    px_x,
                    px_y - terrain._sat_img.get_y_size(),
                    0, 0, -1, -1,
                    (per_step * 0.1) * (task.get_elapsed_frames() + 1)
                )

            terrain._sat_tex.load(terrain._sat_img)

            if task.get_elapsed_frames() < num_steps:
                return task.cont

            if not self._goodenough_activated:
                gray = terrain._sat_img.get_average_gray()
                print("%.1f %% pollinated" % (gray * 100))
                if gray >= PAINT_THRESHOLD:
                    self.enough_paint()

        taskMgr.add(paint_more)


def main():
    game = Game()
    #game.movie(duration=15, fps=30)
    game.run()
