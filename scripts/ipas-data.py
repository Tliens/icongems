#!/usr/bin/env python3
"""Build the IP as Logo (ipaslogo.com) mascot dataset for IconGems.

Source of truth: the ipaslogo.com single-page app embeds a full manifest of
storage keys -> {backgroundColor, width, height}. We extracted it once from
https://ipaslogo.com/assets/index-*.js into a working JSON, then classify each
mascot into one of six categories (animals / nature / food / objects / symbols /
other) from its slug keywords. The upstream Supabase API (which holds the
author's own category + display names) is unreachable from CN networks, so
categories are heuristic — good enough for browsing, and the slug itself is
always shown as the name.

Outputs:
  data/ipas-logos.json  — compact manifest {key: [cat, bg]} + metadata
  (downloads of the webp display images are handled separately; see repo docs)
"""
import json, re, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- keywords --
ANIMALS = set("""
dog cat puppy kitten pup cub inu corgi shiba pug husky akita samoyed beagle collie shepherd malinois labrador retriever spaniel
terrier dachshund schnauzer rottweiler doberman boxer mastiff bulldog poodle papillon chihuahua pomeranian pomsky goldendoodle labradoodle cockapoo
cavapoo bernese newfound boston tzu shih lhasa apso havanese whippet greyhound ridgeback rhodesian vizsla weimaraner basenji
wolf fox fennec dhole dingo jackal coyote raccoon coon badger otter wolverine marten fisher sable
bear panda grizzly sloth
tiger lion leopard jaguar cheetah cougar puma lynx bobcat caracal serval ocelot margay jaguarundi
abyssinian somali bengal siamese burmese ragdoll ragamuffin persian himalayan sphynx devon cornish munchkin scottish
maine siberian norwegian chartreux korat nebelung singapura tonkinese ocicat mau oriental birman turkish angora
cow ox bull calf bison buffalo yak bongo kudu eland oryx ibex markhor tahr goral serow takin moose elk reindeer caribou
horse foal pony donkey mule zebra onager
pig boar peccary babirusa warthog hippo hippopotamus
sheep lamb goat kid alpaca llama guanaco vicuna camel
deer fawn roe sika pudu muntjac muntjac
elephant rhino rhinoceros tapir hyrax manatee dugong
rabbit bunny hare coney pika cottontail jackrabbit
mouse rat squirrel chipmunk marmot beaver gopher vole lemming hamster gerbil jird degu chinchilla viscacha cavy capybara
guinea porcupine hedgehog tenrec shrew mole solenodon desman
kangaroo wallaby wombat koala possum opossum quoll dunnart numbat bilby bandicoot quokka potoroo bettong
bat
gorilla chimpanzee bonobo orangutan gibbon lemur loris bushbaby galago tarsier potto langur macaque baboon mandrill colobus
marmoset tamarin capuchin howler
pangolin armadillo anteater tamandua aardvark
whale dolphin porpoise orca narwhal beluga sperm pilot beaked humpback minke
seal walrus
bird chick duckling duck goose swan teal mallard drake
owl eagle hawk falcon osprey kite harrier vulture condor
penguin puffin auk
parrot macaw cockatoo cockatiel parakeet budgie budgerigar lovebird conure lory lorikeet rosella kakapo kea
finch canary sparrow swallow swift hummingbird kingfisher kookaburra roller hornbill toucan
woodpecker
heron egret stork ibis spoonbill flamingo crane coot moorhen
pelican gannet cormorant frigatebird albatross petrel shearwater skua gull tern plover oystercatcher
avocet curlew godwit sandpiper snipe
pigeon dove crow raven rook jackdaw magpie jay nutcracker
cuckoo roadrunner hoatzin
kiwi cassowary emu rhea ostrich
rooster hen turkey peacock pheasant quail partridge grouse guineafowl
reptile lizard gecko iguana anole chameleon skink monitor komodo
salamander newt axolotl olm hellbender mudpuppy
snake serpent python viper cobra mamba krait taipan racer garter
turtle tortoise terrapin leatherback
crocodile alligator caiman gharial
frog toad treefrog
goldfish koi carp minnow dace chub barb rasbora tetra guppy molly platy swordtail betta gourami cichlid
arowana pufferfish boxfish trunkfish cowfish sunfish opah oarfish
eel moray conger
shark hammerhead thresher mako wobbegong
ray manta stingray skate sawfish torpedo
seahorse pipefish
salmon trout char grayling whitefish pike pickerel perch walleye bass crappie sunfish
catfish loach
tuna mackerel bonito marlin sailfish swordfish barracuda mahi
cod haddock hake anglerfish lanternfish dragonfish hatchetfish barreleye
flounder halibut plaice sole turbot
goby blenny wrasse parrotfish damselfish clownfish anemonefish chromis anthias
triggerfish filefish puffer
grouper snapper grunt drum croaker goatfish mullet flyingfish needlefish
herring sardine anchovy shad smelt capelin
coelacanth sturgeon paddlefish gar bowfin bichir
beetle weevil ladybug ladybird firefly cicada aphid planthopper leafhopper treehopper
ant termite wasp hornet yellowjacket bee bumblebee
butterfly moth skipper caterpillar larva pupa
dragonfly damselfly mayfly stonefly alderfly dobsonfly lacewing antlion
cricket katydid grasshopper locust weta
cockroach mantis earwig silverfish firebrat
flea bedbug assassin stink
fly gnat mosquito midge
spider scorpion tick mite harvestman pseudoscorpion
crab hermit lobster crayfish shrimp prawn krill barnacle copepod
isopod pill
mantis octopus squid cuttlefish nautilus
snail slug nudibranch limpet abalone conch whelk cowrie
clam oyster mussel scallop cockle geoduck
chiton
worm earthworm leech polychaete tubeworm fanworm
flatworm planarian
nematode rotifer
jellyfish hydroid siphonophore salp pyrosome
anemone polyp
starfish urchin cucumber
sponge horseshoe trilobite
aardwolf addax agouti aegirocassis amiskwia amoeba anoa antelope bharal binturong blobfish bontebok bacterium coccus cyanobacterium
choanoflagellate chevrotain coati colugo desmid dinoflagellate dalmatian duiker echidna euglena falanouc ferret foraminifera fossa genet gerenuk
giraffe glaucous glaucus grison hog hound jackalope jerboa kimberella kinkajou klipspringer kowari lancelet linsang loriciferan lumpfish mara
meerkat microspore mitochondrion mudskipper moonfish moonrat naraoia nectocaris okapi opabinia platypus potoo frogmouth qilin ram robin saiga
seadragon sheepdog shoebill skunk springhare scorpionfly snakefly caddisfly booklouse springtail vinegaroon triops tullimonstrum tunicate
tuatara tayra vetulicola weasel webspinner wolpertinger wyvern yapok yeti zorilla placozoan paramecium radiolarian heliozoan stentor volvox
vorticella xenophyophore gastrotrich rotifer tardigrade bdelloid emeraldella hurdia cambroraster titanokorys odaraia tuzoia isoxys leanchoilia
sidneyia sanctacaris waptia hibbertopterus chimera cockatrice griffin hippogriff peryton phoenix centaur hydra kraken selkie kelpie manticore
unicorn dragon sphinx basilisk golem gargoyle
aye dik civet malayan
monkey piglet chicken dormouse maltese mooncalf batfish lanternfly proboscis
mongoose cacomistle coccolithophore angelfish platelet
""".split())

FOOD = set("""
apple banana orange lemon lime peach pear plum apricot cherry strawberry blueberry raspberry blackberry currant gooseberry cranberry
grape mango papaya pineapple kiwi fig date pomegranate lychee rambutan mangosteen persimmon starfruit dragonfruit passion avocado coconut
melon watermelon cantaloupe
tomato potato carrot radish turnip beet yam taro eggplant pepper chili cucumber zucchini squash pumpkin gourd okra artichoke asparagus
broccoli cauliflower cabbage kale lettuce spinach celery leek onion garlic scallion shallot chive
corn pea bean lentil chickpea edamame
wheat rice grain oat barley millet buckwheat
bread toast bagel pretzel croissant brioche baguette ciabatta focaccia sourdough pita naan flatbread mantou bao bun
cake cupcake muffin brownie cookie biscuit cracker waffle pancake crepe donut doughnut pastry danish strudel pie tart cheesecake
custard pudding flan mousse marshmallow mochi dango tangyuan mooncake daifuku
chocolate candy caramel toffee fudge nougat taffy lollipop
gelato sorbet popsicle sundae
sugar jam jelly marmalade syrup molasses
butter cheese yogurt milk kefir
egg omelet
soup ramen pho broth stew curry hotpot fondue
sushi sashimi onigiri nigiri maki bento donburi
dumpling gyoza wonton ravioli pierogi empanada samosa
pizza pasta spaghetti lasagna noodle udon soba vermicelli
taco burrito quesadilla tamale arepa
burger sandwich hotdog panini wrap
bacon ham sausage jerky
salad slaw
popcorn
peanut cashew almond walnut pistachio pecan hazelnut chestnut
coffee espresso latte cappuccino mocha americano macchiato
tea matcha chai oolong
cocoa milkshake smoothie juice lemonade
boba
wine beer sake whisky cocktail
maple
cinnamon vanilla sesame
falafel hummus
churro crumpet scone eclair madeleine financiers canele
wagashi yokan manju senbei
takoyaki okonomiyaki tempura teriyaki yakitori tonkatsu
risotto gnocchi polenta
kebab gyro shawarma
poutine tiffin
miso tofu
pickles pickle kimchi
ketchup mustard mayo
salsa guacamole
flapjack cannoli tagine couscous
arancini au challah loaf macaron pandoro chocolat cacao citrus persimmon
fortune soft salak cream puff
""".split())

NATURE = set("""
tree pine oak maple willow birch cedar fir spruce baobab acacia mangrove
forest woods jungle grove
leaf leaves foliage branch twig sprout seedling sapling shoot bud sprig
flower bloom blossom petal
rose tulip daisy sunflower lily lotus orchid lavender violet iris peony poppy dahlia
dandelion clover edelweiss bluebell primrose foxglove hibiscus gardenia jasmine magnolia camellia
azalea hydrangea wisteria rafflesia protea
monstera pothos fern fiddlehead horsetail moss lichen liverwort
mushroom toadstool fungus agaric morel chanterelle puffball
cactus succulent aloe agave yucca lithops
vine ivy
grass sedge reed bamboo
bush shrub hedge
root tuber bulb rhizome
seed spore pollen
acorn pinecone
ginkgo
mountain hill peak summit ridge cliff mesa plateau
valley canyon gorge
cave cavern grotto
volcano lava magma crater geyser
rock stone boulder pebble cobble
clay soil earth mud
crystal quartz geode amethyst agate jade obsidian granite marble
mineral gem gemstone
river stream creek waterfall
lake pond pool puddle lagoon
ocean sea bay cove gulf estuary atoll reef
shore beach coast dune
tide tidepool
wave swell surf ripple
spring oasis
island islet archipelago cay
desert
meadow field prairie steppe savanna tundra heath moor marsh swamp bog fen wetland
cloud raincloud thundercloud
rain drizzle storm thunderstorm
snow snowflake snowdrift frost ice icicle hail
fog mist haze
dew dewdrop droplet
rainbow aurora halo
lightning thunder
wind breeze gale gust cyclone typhoon tornado
sun sunshine sunrise sunset dawn dusk twilight
moon luna lunar crescent
star starlight stardust constellation
comet meteor asteroid
planet saturn jupiter mars venus mercury neptune uranus
galaxy nebula cosmos universe
eclipse solstice
orbit
amber resin
seashell shell conch
kelp seaweed algae plankton diatom
coral
pearl
season winter
bladderwort butterwort sundew flytrap venus bonsai raindrop diamond moonstone rosette
welwitschia plant pitcher sensitive campfire pulsar water drop
""".split())

OBJECTS = set("""
robot bot mech android droid
clock watch alarm chronometer chronograph hourglass sundial timer
map atlas globe compass sextant astrolabe armillary orrery telescope binoculars microscope magnifier lens prism
camera film projector phonograph gramophone radio television monitor screen
phone telephone smartphone pager walkie
computer laptop keyboard keycap mouse trackball joystick controller printer scanner
headphones speaker microphone megaphone
battery plug cable charger
lightbulb lamp lantern torch flashlight candle lighthouse beacon
mirror easel
book notebook journal scroll parchment newspaper magazine letter envelope stamp postcard parcel package
pen pencil quill paintbrush marker crayon chalk ink inkstone eraser ruler protractor caliper
scissors knife sword dagger axe saw hammer mallet drill screwdriver wrench pliers clamp vise chisel file rasp adze froe brayer
needle thread yarn knitting crochet loom shuttle spindle
toolbox workbench anvil forge bellows crucible
pot jar bottle flask beaker petri vial
kettle teapot mug bowl plate dish saucer platter tray
pan wok skillet grill oven stove cooker microwave toaster blender mixer juicer grinder mortar pestle
spoon fork chopstick spatula ladle whisk tongs strainer sieve colander shaker
refrigerator cupboard shelf drawer cabinet
chair stool bench sofa table desk dresser wardrobe armoire bookcase
bed pillow blanket quilt
rug carpet curtain
fan humidifier vacuum broom mop dustpan duster laundry
soap towel sponge
toothbrush comb razor
shirt coat jacket cap boot shoe sock glove scarf mitten apron
button zipper pocket collar
fabric cloth denim leather canvas linen silk
sewing
purse wallet backpack suitcase satchel handbag
umbrella cane staff pole
ring necklace bracelet brooch pendant earrings tiara crown
coin currency treasure vault safe
lock padlock keyhole bolt latch
chain rope cord string ribbon
wheel gear cog pulley lever crank axle bearing coil
engine motor turbine generator reactor
magnet
scale balance meter gauge barometer anemometer seismograph oscilloscope thermometer
pump valve pipe hose nozzle faucet
ladder stair escalator elevator
bridge tunnel tower pagoda shrine gate archway column pillar obelisk
house cabin cottage hut barn castle fortress palace temple cathedral
building factory warehouse
window door gate roof wall floor
street road path lane sidewalk
fountain statue monument
car bus van truck taxi trolleybus tram train locomotive railway subway metro
carriage wagon cart sled chariot
bicycle bike scooter motorcycle skateboard hoverboard
boat ship sailboat tugboat ferry canoe kayak raft gondola barge yacht submarine submersible bathysphere
airplane jet glider helicopter airship zeppelin balloon blimp drone
rocket spacecraft spaceship starship shuttle lander rover satellite station capsule probe
harbor dock pier
streetlamp sign signal
hydrant mailbox
firetruck ambulance
tractor plow mower wheelbarrow spade shovel hoe rake pitchfork
waterwheel windmill quern
shield armor helmet bow arrow spear lance mace club
piano organ accordion harmonica
violin viola cello fiddle erhu sitar shamisen banjo guitar ukulele mandolin harp lyre zither koto
flute piccolo recorder ocarina clarinet oboe bassoon saxophone trumpet trombone horn tuba bugle
drum tambourine maracas cabasa conga bongo cymbals gong bell handbell chime xylophone glockenspiel marimba vibraphone kalimba
metronome
bagpipes castanets guiro woodblock
cassette tape vinyl
amplifier
game toy doll puppet marionette kite yo
balloon pinata gift
football soccer basketball baseball tennis golf rugby volleyball bowling
racket bat cue puck
trophy badge
flag banner
skate ski surfboard paddle oar
whistle
library museum
label tag
ornament
recycle
cage aquarium terrarium greenhouse
planter vase urn
shears hose sprinkler
abacus balalaika binder beehive skep bookend bollard canteen carousel cauldron centrifuge circuit clip clothespin corkscrew counter
cowbell desktop disk floppy dome doorbell doorstop drawknife funicular gatehouse geiger glass goggles gyroscope handpan kaleidoscope kettlebell
lunchbox monorail moonbase observatory paper paperclip pincushion pushpin periscope plumb plunger potholder reamer router slide sneaker
slippers snowplow stapler stirrer teacup theodolite thermos thimble trivet trowel typewriter voltmeter bongos maul last wheelbarrow
racket sandbox key calculator measuring rolling watering bucket caravan
hole puncher punch traffic vane retort hotplate dovecote hamper takeout opener recycling adding soldering iron plane spokeshave pod
ramekin ferryboat triangle microcassette
""".split())

SYMBOLS = set("""
ghost spirit phantom specter wraith
fairy fae sprite pixie elf gnome goblin ogre troll imp demon devil djinn genie jinn
gremlin
angel cherub
wizard witch mage sorcerer warlock enchanter necromancer alchemist apothecary oracle seer mystic shaman druid
knight guardian sentinel protector warden keeper watcher hunter scout
king queen prince princess lord liege jester
cowboy sheriff bandit pirate sailor captain admiral courier messenger traveler wanderer
chef baker barber blacksmith mason carpenter cobbler tailor weaver potter smith mender decorator curator librarian archivist secretary scribe
elemental flame ember blaze
spell spellbook charm rune sigil glyph talisman amulet potion elixir
portal dimension rift gateway
aura halo
soul essence wisp shade echo shadow
dream nightmare vision reverie
idea insight wisdom knowledge
infinity unity harmony balance
heart love peace hope faith luck fortune destiny fate
atom molecule quantum plasma particle electron proton neutron nucleus cell organelle vacuole lysosome chloroplast membrane
helix
dreamcatcher
zodiac horoscope
tarot omen divination
myth mythic legend folklore
artifact relic
avatar persona mask identity
emblem crest
cipher code password
arcane occult esoteric
totem
familiar
deity god goddess titan
astral ethereal
underworld
reincarnation resurrection
mana
spectrum phase vortex spiral singularity
wormhole
speech note domovoi carbuncle tooth
""".split())

# never classify on these (colors, poses, anatomy, geography, series markers)
SKIP = set("""
left right face head eye eyes ear ears cheek cheeks mouth nose forehead muzzle body wing tail paw hoof tooth
small tiny large big compact mini miniature giant broad wide tall short long
round rounded oval pointy square soft gentle calm peaceful serene quiet shy curious cheerful happy smiling smile playful friendly fluffy plump chubby
sleepy alert watchful
baby young old
red blue green yellow orange purple pink magenta brown gray grey white black ivory golden silver cyan teal indigo violet ochre burgundy cobalt
warm cool bright dark pale muted deep light
classic standard
low high close open peek hiding peeking
inspired style series set variant
bg c a1 a2 a3 a4 a5 a6 a7 a8 a9
american australian british chinese japanese italian french russian german english egyptian african european asian arctic alpine himalayan siberian
sichuan malayan southern northern western eastern exotic domestic wild city desert forest ocean space
music musical note string brass woodwind percussion
the of and with two four covered potted
african baby bright calm cheerful curious eared english eyed friendly gentle habitat long lowland nosed old patagonian playful shy smile southern
tiny warm musical stealth wonder creature night magnetic analog titan potential resilience empath kindness curiosity
""".split())

ORDER = ('animals', 'food', 'nature', 'symbols', 'objects')

def classify(slug: str) -> str:
    words = slug.split('-')
    if words and words[-1].isdigit():
        words = words[:-1]
    sets = {'animals': ANIMALS, 'food': FOOD, 'nature': NATURE, 'symbols': SYMBOLS, 'objects': OBJECTS}
    for cat in ORDER:
        for w in words:
            if w in sets[cat]:
                return cat
    return 'other'

def display_name(key: str) -> str:
    slug = key.split('-', 1)[1] if '-' in key else key
    slug = re.sub(r'-(\d+)$', r' \1', slug)
    return ' '.join(p.upper() if len(p) <= 2 and p[-1].isdigit() or p in ('a1','a2','a3','a4','a5','a6','a7','a8','a9') else p.capitalize()
                    for p in slug.split('-'))

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ipas-manifest.json'
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'data', 'ipas-logos.json')
    manifest = json.load(open(src))
    logos, dist = {}, Counter()
    other_samples = []
    for key, meta in manifest.items():
        slug = key.split('-', 1)[1] if '-' in key else key
        slug = re.sub(r'-\d+$', '', slug)
        cat = classify(slug)
        logos[key] = [cat, meta['bg']]
        dist[cat] += 1
        if cat == 'other' and len(other_samples) < 80:
            other_samples.append(slug)
    data = {
        'site': 'IP as Logo',
        'source': 'https://ipaslogo.com/',
        'source_cdn': 'https://cdn.ipaslogo.com',
        'license': 'MIT (github.com/s1dashu/ip-as-logo-skill) — free mascot logos',
        'note': 'categories are heuristic (keyword-derived); names are slug-derived',
        'count': len(logos),
        'cats': ['animals', 'nature', 'food', 'objects', 'symbols', 'other'],
        'cat_counts': dict(dist),
        'logos': logos,
    }
    json.dump(data, open(out, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('distribution:', dict(dist))
    print('other samples:', ' '.join(other_samples[:80]))
    print('wrote', out, os.path.getsize(out), 'bytes')

if __name__ == '__main__':
    main()
