from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

load_dotenv()

# We need a dummy app context for Bcrypt if used this way, 
# or we can just use a simple hash. Let's use Bcrypt for consistency.
app = Flask(__name__)
bcrypt = Bcrypt(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.agroassist

# Structured Expert-Grade Crop Data with Daily Routine Snapshots
CROP_ROUTINES_DATA = [
    {
        "name": "Rice",
        "category": "Grain",
        "image": "/crops/rice.jpg",
        "growing_season": "Summer/Kharif",
        "avg_duration": "120-150 Days",
        "soil_preference": "Alluvial/Clay",
        "water_requirement": "High",
        "cultivation_guide": {
            "soil_preparation": "Deep plowing followed by puddling is essential for moisture retention and weed control.",
            "irrigation_guidance": "Maintains standing water of 2-5cm during the vegetative stage. Drain only before harvest.",
            "fertilizer_practices": "NPK ratio of 120:60:40 kg/ha. Apply Urea in three split doses for maximum nitrogen efficiency.",
            "seasonal_tips": "Transplant seedlings early in the season to leverage early monsoon and avoid peak pest cycles."
        },
        "pests_diseases": [
            {
                "name": "Stem Borer",
                "symptoms": "Presence of 'dead hearts' in young plants and 'whiteheads' in older ones.",
                "causes": "Larvae of Scirpophaga incertulas boring into the stem.",
                "risk_stage": "Tillering to Panicle Initiation",
                "prevention": "Systematic removal of stubbles after harvest and using pheromone traps.",
                "treatment": "Application of Cartap Hydrochloride or Carbofuran at the first sign of infestation.",
                "risk_level": "High"
            },
            {
                "name": "Bacterial Leaf Blight",
                "symptoms": "Water-soaked streaks that turn yellow and eventually white starting from leaf tips.",
                "causes": "Xanthomonas oryzae bacteria spread through wind and rain.",
                "risk_stage": "Maximum Tillering to Flowering",
                "prevention": "Avoid over-fertilization of nitrogen and use resistant varieties.",
                "treatment": "Spray Streptocycline mixed with Copper Oxychloride.",
                "risk_level": "Critical"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "BPH Outbreak Warning",
                "msg": "Brown Plant Hopper activity detected in nearby regions. Inspect base of plants immediately."
            },
            {
                "type": "Weather",
                "title": "Flash Flood Risk",
                "msg": "Heavy rainfall predicted for the next 48 hours. Ensure field drainage channels are clear."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 10, "title": "Nursery Preparation", 
                "desc": "Sow seeds in nursery beds with high moisture and organic mulch.", 
                "protocol": "Use high-quality certified seeds. Treat seeds with Carbendazim. Maintain organic mulch.",
                "risk": "High humidity may trigger damping-off disease. Avoid over-watering.",
                "daily_routine": ["Check nursery moisture levels", "Remove any competitive weeds", "Inspect for fungal spots"]
            },
            {
                "start_day": 25, "end_day": 30, "title": "Transplanting", 
                "desc": "Transfer seedlings to puddled fields with 20x15cm spacing.", 
                "protocol": "Ensure perfect puddling. Maintain 2-3 cm standing water. Even spacing.",
                "risk": "Transplant shock. Ensure seedlings are handled gently to avoid root damage.",
                "daily_routine": ["Monitor water standing level", "Check seedling verticality", "Observe for uprooted plants"]
            },
            {
                "start_day": 31, "end_day": 56, "title": "Tillering Stage", 
                "desc": "Maintain 5cm water levels and apply first dose of Nitrogen.", 
                "protocol": "Top dressing of Urea is critical. Keep water level consistent to suppress weeds.",
                "risk": "Monitor for Stem Borer activity. Look for dead hearts in the tillers.",
                "daily_routine": ["Inspect tillers for dead hearts", "Maintain 5cm water depth", "Clean field borders of weeds"]
            },
            {
                "start_day": 80, "end_day": 90, "title": "Panicle Initiation", 
                "desc": "Critical water stage. Avoid moisture stress at all costs.", 
                "protocol": "Most sensitive stage for water. Maintain constant flooding.",
                "risk": "Bacterial Leaf Blight risk increases with heavy rain/wind. Check for yellow streaks.",
                "daily_routine": ["Ensure no water stress", "Look for yellow leaf streaks", "Monitor weather for rain/wind"]
            },
            {
                "start_day": 110, "end_day": 120, "title": "Harvesting", 
                "desc": "Drain water 10 days before harvest. Harvest when 80% grains turn golden.", 
                "protocol": "Late drainage helps ripening. Use sharp sickles. Dry grains to 12% moisture.",
                "risk": "Delayed harvest may lead to grain shattering or bird damage.",
                "daily_routine": ["Check grain moisture/color", "Identify optimal harvest spots", "Clean harvesting tools"]
            }
        ],
        "post_harvest": {
            "storage": "Store grains in cool, dry gunny bags. Maintain 12% moisture to prevent mold.",
            "cleaning": "Remove all stubble immediately to disrupt life cycles of overwintering stem borers.",
            "soil_prep": "Prepare for wheat or legumes by deep plowing to expose pathogens to sunlight.",
            "residue": "Incorporate residue into soil or use for mulching. Avoid field burning."
        }
    },
    {
        "name": "Wheat",
        "category": "Grain",
        "image": "/crops/Wheat.jpg",
        "growing_season": "Winter/Rabi",
        "avg_duration": "120-130 Days",
        "soil_preference": "Loamy/Well-drained",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Fine tilth is required. Disc harrow followed by cultivator and planking.",
            "irrigation_guidance": "6 irrigations are standard. CRI stage (21 days) is the most critical.",
            "fertilizer_practices": "NPK 120:60:40. Phosphorus and Potash as basal; Nitrogen in 2 split doses.",
            "seasonal_tips": "Maintain low temperatures during grain filling for higher carbohydrate accumulation."
        },
        "pests_diseases": [
            {
                "name": "Yellow Rust",
                "symptoms": "Yellow streaks of pustules on leaves that rub off as orange-yellow powder.",
                "causes": "Puccinia striiformis fungus thriving in cool, humid conditions.",
                "risk_stage": "Jointing to Boot stage",
                "prevention": "Sow early-maturing and resistant varieties.",
                "treatment": "Spray Propiconazole (Tilt) @ 500ml/ha.",
                "risk_level": "Critical"
            },
            {
                "name": "Aphids",
                "symptoms": "Clusters of green insects on spikes, sticky honeydew appearance.",
                "causes": "Small sucking insects extracting sap from the grain heads.",
                "risk_stage": "Milking to Soft Dough",
                "prevention": "Maintain adequate bird populations or use sticky traps.",
                "treatment": "Spray Imidacloprid if populations exceed economic threshold.",
                "risk_level": "Moderate"
            }
        ],
        "active_alerts": [
            {
                "type": "Disease",
                "title": "Rust Index High",
                "msg": "Cool morning dew and temperatures favoring Rust spread. Scout fields daily."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 5, "title": "Sowing", 
                "desc": "Direct sowing in well-pulverized soil at 5cm depth.", 
                "protocol": "Ensure 'vapsa' soil condition. Use seed drill for 22.5cm row spacing.",
                "risk": "Termite attack in dry soil. Treat seeds with Chlorpyriphos if history of termites.",
                "daily_routine": ["Monitor soil moisture", "Check for termite tracks", "Keep field clear of birds"]
            },
            {
                "start_day": 21, "end_day": 21, "title": "CRI Stage", 
                "desc": "Crown Root Initiation. Most critical period for first irrigation.", 
                "protocol": "Apply first irrigation exactly at 21 days for optimal root development.",
                "risk": "Skipping irrigation now can reduce yield by up to 30%.",
                "daily_routine": ["Apply first irrigation", "Check for crown root growth", "Prepare for Nitrogen dose"]
            },
            {
                "start_day": 42, "end_day": 56, "title": "Jointing", 
                "desc": "Apply Urea and ensure field is clear of weeds.", 
                "protocol": "Second Nitrogen dose. Monitor for Yellow Rust during cool, humid mornings.",
                "risk": "Yellow Rust can spread rapidly. Check for orange-yellow pustules on leaves.",
                "daily_routine": ["Scout for rust on leaves", "Remove deep-rooted weeds", "Apply scheduled fertilizer"]
            },
            {
                "start_day": 98, "end_day": 105, "title": "Milking Stage", 
                "desc": "Final irrigation phase. Protect from late-season heat waves.", 
                "protocol": "Light irrigation for canopy cooling. Avoid drought at this stage.",
                "risk": "Aphid infestation. Look for sticky honey-dew on the spikes.",
                "daily_routine": ["Light morning irrigation", "Check spikes for aphids", "Monitor afternoon heat"]
            },
            {
                "start_day": 120, "end_day": 130, "title": "Harvesting", 
                "desc": "Harvest when moisture content drops to 14-15%.", 
                "protocol": "Harvest when grains produce a 'clicking' sound when bitten.",
                "risk": "Pre-harvest rain can cause grain sprouting in the ear.",
                "daily_routine": ["Bite grains to test hardness", "Check weather for dry 3-day window", "Seal storage bags"]
            }
        ],
        "post_harvest": {
            "storage": "Store in airtight bins or silos. Protect from humidity and grain-weevils.",
            "cleaning": "Clear field of any infected debris to prevent rust spores from lingering.",
            "soil_prep": "Focus on moisture conservation for the upcoming summer fallow or pulse crop.",
            "residue": "Wheat straw can be used as high-quality cattle fodder or mushroom substrate."
        }
    },
    {
        "name": "Maize",
        "category": "Grain",
        "image": "/crops/Maize.jpg",
        "growing_season": "Kharif/Summer",
        "avg_duration": "90-110 Days",
        "soil_preference": "Deep Loamy",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Plough the field twice for fine tilth. Ensure adequate drainage as maize is sensitive to waterlogging.",
            "irrigation_guidance": "Kneehigh stage and silking stage are critical for water. Avoid stress during pollination.",
            "fertilizer_practices": "Balanced application of NPK (120:60:40). Zinc deficiency is common; apply ZnSO4 if needed.",
            "seasonal_tips": "Sow with the onset of monsoon for Kharif or early Feb for spring crop."
        },
        "pests_diseases": [
            {
                "name": "Fall Armyworm",
                "symptoms": "Ragged holes in leaves and presence of sawdust-like excrement in the whorls.",
                "causes": "Spodoptera frugiperda larvae feeding on the whorl.",
                "risk_stage": "Early Vegetative to Tasseling",
                "prevention": "Intercropping with legumes and using bird perches.",
                "treatment": "Spray Emamectin benzoate or Spinetoram.",
                "risk_level": "Critical"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "Armyworm Warning",
                "msg": "High FAW activity reported in Western UP. Inspect whorls for fresh damage."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 15, "title": "Establishment", 
                "desc": "Seedling emergence and early vigor management.", 
                "protocol": "Sow at 3-5cm depth. Ensure soil moisture. Gap filling if needed.",
                "risk": "Bird damage and soil pests like crickets.",
                "daily_routine": ["Monitor emergence", "Check for gap filling", "Inspect for soil pests"]
            },
            {
                "start_day": 30, "end_day": 45, "title": "Kneehigh Stage", 
                "desc": "Rapid vegetative growth. Apply first top dressing of Nitrogen.", 
                "protocol": "Earthing up to prevent lodging. Apply 1/3 Nitrogen dose.",
                "risk": "Stem borer and weed competition.",
                "daily_routine": ["Earthing up", "Apply Nitrogen fertilizer", "Check for whorl damage"]
            },
            {
                "start_day": 65, "end_day": 80, "title": "Silking/Tasseling", 
                "desc": "Pollination stage. Critical for water and nutrients.", 
                "protocol": "Maintain soil moisture at capacity. No stress during pollination.",
                "risk": "Drought stress leads to poor grain filling.",
                "daily_routine": ["Ensure full irrigation", "Monitor pollen shedding", "Observe silk health"]
            }
        ],
        "post_harvest": {
            "storage": "Dry cobs to 12% moisture. Store in ventilated metal bins.",
            "cleaning": "Shred stalks and incorporate for organic matter.",
            "soil_prep": "Prepare for Mustard or Wheat by leveling and deep plowing.",
            "residue": "Stover is excellent for silage or fuel."
        }
    },
    {
        "name": "Potato",
        "category": "Vegetable",
        "image": "/crops/Potato.jpg",
        "growing_season": "Winter/Rabi",
        "avg_duration": "90-120 Days",
        "soil_preference": "Loose Sandy Loam",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Loose, well-aerated soil is required for tuber expansion. Ridges and furrows are best.",
            "irrigation_guidance": "Frequent light irrigations. Stop irrigation 10-15 days before harvest for skin hardening.",
            "fertilizer_practices": "High potash requirement for tuber size. Split Urea doses.",
            "seasonal_tips": "Use fungicide-treated seed tubers to prevent early blight."
        },
        "pests_diseases": [
            {
                "name": "Late Blight",
                "symptoms": "Dark, water-soaked patches on leaves that turn brown/black. White mold on underside.",
                "causes": "Phytophthora infestans fungus during humid/cool weather.",
                "risk_stage": "Vegetative to Tuberization",
                "prevention": "Row spacing for airflow and balanced Nitrogen.",
                "treatment": "Prophylactic spray of Mancozeb or systemic Metalaxyl.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Weather",
                "title": "Frost Alert",
                "msg": "Severe frost expected tonight. Irrigate immediately to protect potato vines."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 20, "title": "Sprouting", 
                "desc": "Tuber germination and emergence.", 
                "protocol": "Plant pre-sprouted tubers. Maintain ridge integrity.",
                "risk": "Seed piece decay in overly wet soil.",
                "daily_routine": ["Check ridge moisture", "Monitor emergence rate", "Observe for fungal rot"]
            },
            {
                "start_day": 40, "end_day": 60, "title": "Tuber Initiation", 
                "desc": "Stolons swell into tubers. High nutrient demand.", 
                "protocol": "Earthing up to cover growing tubers. Apply Potash dose.",
                "risk": "Early blight and aphids.",
                "daily_routine": ["Mound soil around stems", "Inspect for leaf spots", "Monitor aphid count"]
            },
            {
                "start_day": 85, "end_day": 100, "title": "Stalk Cutting", 
                "desc": "Haulm cutting to harden potato skin before digging.", 
                "protocol": "Cut vines 10 days before harvest. Stop water.",
                "risk": "Tuber moth infestation if tubers are exposed.",
                "daily_routine": ["Cut old stalks", "Ensure no tuber exposure", "Final field check"]
            }
        ],
        "post_harvest": {
            "storage": "Store in cold storage at 4°C for seeds or ventilated dark room for table use.",
            "cleaning": "Remove all rotten tubers to prevent spread of soft rot.",
            "soil_prep": "Follow with green manure or summer vegetables.",
            "residue": "Potato vines can be composted."
        }
    },
    {
        "name": "Cotton",
        "category": "Commercial",
        "image": "/crops/Cotton.jpg",
        "routine": [
            {
                "start_day": 1, "end_day": 7, "title": "Pre-sowing", 
                "desc": "Deep plowing and soil solarization to kill soil-borne pests.", 
                "protocol": "Plow 20-25cm deep. Seed treatment with Imidacloprid.",
                "risk": "Early season Jassids and Thrips. Monitor seedlings closely.",
                "daily_routine": ["Clean field of debris", "Check soil temperature", "Calibrate seed drill"]
            },
            {
                "start_day": 15, "end_day": 20, "title": "Thinning", 
                "desc": "Remove weak seedlings and maintain optimal plant population.", 
                "protocol": "Maintain 60k-80k plants/ha. Remove symptomatic viral plants.",
                "risk": "Overcrowding leads to poor airflow and high pest incidence.",
                "daily_routine": ["Uproot stunted seedlings", "Maintain uniform spacing", "Check for sucking pests"]
            },
            {
                "start_day": 42, "end_day": 70, "title": "Square Formation", 
                "desc": "Monitor for pink bollworm and apply potash for fiber strength.", 
                "protocol": "Spray MOP @ 1%. Use pheromone traps for monitoring.",
                "risk": "Pink Bollworm (PBW) alert. If more than 5 moths/trap, apply insecticide.",
                "daily_routine": ["Check pheromone traps", "Look for 'rosette' flowers", "Apply light foliar spray"]
            },
            {
                "start_day": 84, "end_day": 112, "title": "Boll Bursting", 
                "desc": "Ensure dry weather and stop irrigation to facilitate boll opening.", 
                "protocol": "Stop irrigation after 25% boll opening. High MOP dose improves fiber.",
                "risk": "Boll Rot due to high humidity or late rain. Avoid excessive Nitrogen.",
                "daily_routine": ["Identify opened bolls", "Prune lower dry leaves", "Monitor for boll rot"]
            },
            {
                "start_day": 140, "end_day": 160, "title": "Picking", 
                "desc": "Pick opened bolls in dry conditions to maintain cotton quality.", 
                "protocol": "Pick after 10 AM. Grade based on cleanliness.",
                "risk": "Contamination with dry leaves/bracts reduces market grade significantly.",
                "daily_routine": ["Pick manually after 10 AM", "Sort by fiber quality", "Sun-dry picked cotton"]
            }
        ]
    },
    {
        "name": "Sugarcane",
        "category": "Commercial",
        "image": "/crops/Sugarcane.jpg",
        "growing_season": "Annual",
        "avg_duration": "10-14 Months",
        "soil_preference": "Heavy Clay/Loam",
        "water_requirement": "Very High",
        "cultivation_guide": {
            "soil_preparation": "Deep subsoiling is necessary to break hard pans. Apply heavy organic manure.",
            "irrigation_guidance": "Sugarcane is a thirsty crop. Flood irrigation or subsurface drip is effective.",
            "fertilizer_practices": "Heavy Nitrogen feeder. Apply in split doses across 6 months.",
            "seasonal_tips": "Intercropping with pulses in early stages can provide extra income."
        },
        "pests_diseases": [
            {
                "name": "Red Rot",
                "symptoms": "Reddish discoloration inside stalks and withering of leaves.",
                "causes": "Colletotrichum falcatum fungus.",
                "risk_stage": "Maturity Stage",
                "prevention": "Use disease-free sets and avoid waterlogging.",
                "treatment": "Uproot infected clumps and apply lime.",
                "risk_level": "Critical"
            }
        ],
        "active_alerts": [
            {
                "type": "Weather",
                "title": "Heat Wave Warning",
                "msg": "Temperatures exceeding 45°C. Increase irrigation frequency to prevent leaf scorch."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 30, "title": "Planting", 
                "desc": "Set placement in furrows with 75-90cm spacing.", 
                "protocol": "Treat sets with hot water or fungicide. Ensure eye buds face upward.",
                "risk": "Termite attack on sets.",
                "daily_routine": ["Monitor eye-bud sprouting", "Look for termite tunnels", "Light irrigation"]
            },
            {
                "start_day": 120, "end_day": 180, "title": "Grand Growth", 
                "desc": "Rapid internode elongation and sugar accumulation.", 
                "protocol": "Heavy irrigation. Earthing up to prevent lodging. Propping if necessary.",
                "risk": "Top borer and internode borer.",
                "daily_routine": ["Ensure constant moisture", "Check for top borer", "De-trashing old leaves"]
            }
        ],
        "post_harvest": {
            "storage": "Must be crushed within 24 hours of harvest to prevent sugar loss.",
            "cleaning": "Remove dry leaves and trash from harvested stalks.",
            "soil_prep": "Ratoon crop management starts immediately.",
            "residue": "Sugarcane trash can be used for electricity generation or mulching."
        }
    },
    {
        "name": "Tomato",
        "category": "Vegetable",
        "image": "/crops/tomato.jpg",
        "growing_season": "Rabi/Summer",
        "avg_duration": "100-120 Days",
        "soil_preference": "Well-drained Loamy Soil",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Plough field to fine tilth. Apply 20 t/ha FYM basal.",
            "irrigation_guidance": "Regular intervals. Avoid waterlogging. Drip irrigation preferred.",
            "fertilizer_practices": "NPK 150:100:50. Top dress Nitrogen in 3 splits.",
            "seasonal_tips": "Staking is essential for indeterminate varieties to prevent fruit rot."
        },
        "pests_diseases": [
            {
                "name": "Early Blight",
                "symptoms": "Concentric rings on lower leaves; yellowing and defoliation.",
                "causes": "Alternaria solani fungus.",
                "risk_stage": "Vegetative to Fruiting",
                "prevention": "Crop rotation and spacing for airflow.",
                "treatment": "Spray Mancozeb or Chlorothalonil.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Weather",
                "title": "Humidity Spike",
                "msg": "High humidity predicted. Scout for Blight symptoms immediately."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 25, "title": "Nursery", 
                "desc": "Grow seedlings in raised beds or pro-trays.", 
                "protocol": "Protect from heavy rain. Use insect-proof nets.",
                "risk": "Damping-off in wet conditions.",
                "daily_routine": ["Misty irrigation", "Check for wilting", "Inspect for whiteflies"]
            },
            {
                "start_day": 60, "end_day": 90, "title": "Fruiting", 
                "desc": "Fruit setting and ripening phase.", 
                "protocol": "Apply Calcium to prevent Blossom End Rot. Prune lower leaves.",
                "risk": "Fruit borer and Blossom End Rot.",
                "daily_routine": ["Fruit borer check", "Apply liquid nutrients", "Staking check"]
            }
        ],
        "post_harvest": {
            "storage": "Store at 10-12°C for long shelf life. Grade by size and color.",
            "cleaning": "Wipe with soft cloth; remove damaged fruits.",
            "soil_prep": "Follow with legumes to restore nitrogen.",
            "residue": "Compost healthy vines; burn diseased ones."
        }
    },
    {
        "name": "Mustard",
        "category": "Oilseed",
        "image": "/crops/Mustard.jpg",
        "growing_season": "Winter/Rabi",
        "avg_duration": "110-140 Days",
        "soil_preference": "Loamy/Saline tolerant",
        "water_requirement": "Low",
        "cultivation_guide": {
            "soil_preparation": "Fine seedbed is required for uniform germination of small mustard seeds.",
            "irrigation_guidance": "Only 2-3 irrigations needed. Flowering and siliqua filling are critical.",
            "fertilizer_practices": "Sulfur application is critical for oil content. Apply Elemental Sulfur.",
            "seasonal_tips": "Sow when night temperatures dip below 15°C for best growth."
        },
        "pests_diseases": [
            {
                "name": "Aphids",
                "symptoms": "Curling of leaves and presence of green/black tiny insects.",
                "causes": "Lipaphis erysimi sucking sap from tender parts.",
                "risk_stage": "Flowering to Pod Formation",
                "prevention": "Early sowing and light trap usage.",
                "treatment": "Spray Neem oil or Thiamethoxam during evening.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "Aphid Surge",
                "msg": "Mild humid weather predicted, ideal for aphid explosion. Spray Neem oil protectively."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 10, "title": "Sowing", 
                "desc": "Sow in lines using seed drill at 45cm spacing.", 
                "protocol": "Mix seeds with sand for even distribution. Maintain shallow depth.",
                "risk": "Crust formation preventing emergence.",
                "daily_routine": ["Monitor emergence", "Check for soil crusting", "Identify ant activity"]
            },
            {
                "start_day": 40, "end_day": 60, "title": "Flowering", 
                "desc": "Yellow bloom stage. High bee activity is beneficial.", 
                "protocol": "Avoid pesticide spray to protect pollinators. Light irrigation if dry.",
                "risk": "Aphid colonies formation on flowers.",
                "daily_routine": ["Inspect flower heads for aphids", "Monitor bee activity", "Check soil moisture"]
            }
        ],
        "post_harvest": {
            "storage": "Dry seeds until they crackle when pressed. Store in moisture-proof containers.",
            "cleaning": "Winnowing to remove dust and empty pods.",
            "soil_prep": "Prepare for Kharif maize or cotton.",
            "residue": "Mustard stalks can be used for heating or compost."
        }
    },
    {
        "name": "Banana",
        "category": "Fruit",
        "image": "/crops/banana.jpg",
        "growing_season": "Annual/Perennial",
        "avg_duration": "10-12 Months",
        "soil_preference": "Fertile, Well-drained Loam",
        "water_requirement": "Very High",
        "cultivation_guide": {
            "soil_preparation": "Deep plowing and incorporation of heavy organic matter (manure). Dig pits of 45x45x45cm.",
            "irrigation_guidance": "Requires constant moisture. Drip irrigation is highly recommended for water efficiency.",
            "fertilizer_practices": "Heavy feeder of Nitrogen and Potash. Apply in 4-6 split doses.",
            "seasonal_tips": "Protect from high winds using windbreaks. Desuckering is essential for fruit quality."
        },
        "pests_diseases": [
            {
                "name": "Panama Wilt",
                "symptoms": "Yellowing of lower leaves and splitting of pseudo-stem base.",
                "causes": "Fusarium oxysporum fungus.",
                "risk_stage": "Vegetative Stage",
                "prevention": "Use disease-free suckers and avoid waterlogging.",
                "treatment": "Uproot infected plants and treat soil with Carbendazim.",
                "risk_level": "Critical"
            }
        ],
        "active_alerts": [
            {
                "type": "Weather",
                "title": "Strong Wind Warning",
                "msg": "High winds predicted. Ensure prop supports for heavy fruiting bunches."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 30, "title": "Planting", 
                "desc": "Plant suckers in prepared pits with rich organic base.", 
                "protocol": "Select sword suckers. Trim old roots. Maintain upright position.",
                "risk": "Root rot in overly wet soil.",
                "daily_routine": ["Monitor sucker establishment", "Check soil moisture around pits", "Look for early leaf spots"]
            },
            {
                "start_day": 150, "end_day": 180, "title": "Bunch Emergence", 
                "desc": "Propping and protection of emerging fruit bunches.", 
                "protocol": "Provide bamboo support. Remove male buds after bunch completion.",
                "risk": "Bunch breakage due to weight.",
                "daily_routine": ["Check propping stability", "Remove male buds", "Inspect for fruit scarring"]
            }
        ],
        "post_harvest": {
            "storage": "Harvest at 75-80% maturity for long-distance transport. Store in ventilated crates.",
            "cleaning": "Wash bunches in chlorine water to remove dirt and insects.",
            "soil_prep": "Intercrop with vegetables for extra income during the first phase.",
            "residue": "Pseudostems can be used for fiber or specialized compost."
        }
    },
    {
        "name": "Soybean",
        "category": "Oilseed",
        "image": "/crops/Soybean.jpg",
        "growing_season": "Kharif",
        "avg_duration": "90-110 Days",
        "soil_preference": "Well-drained Loamy/Clayey",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Fine tilth is required. Level the field properly to avoid waterlogging.",
            "irrigation_guidance": "Critical stages are flowering and pod filling. Drought stress during these times reduces yield.",
            "fertilizer_practices": "Basal dose of NPK (20:60:40). Seed treatment with Rhizobium is crucial for nitrogen fixation.",
            "seasonal_tips": "Avoid sowing if soil is too wet to prevent seed rot."
        },
        "pests_diseases": [
            {
                "name": "Yellow Mosaic Virus",
                "symptoms": "Bright yellow patches on leaves; plants become stunted.",
                "causes": "Virus spread by Whiteflies.",
                "risk_stage": "Found throughout growth",
                "prevention": "Use resistant varieties and control whitefly populations.",
                "treatment": "Spray systemic insecticides like Acetamiprid.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "Whitefly Alert",
                "msg": "Increased whitefly count in local traps. Inspect soybean fields for YMV symptoms."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 15, "title": "Sowing", 
                "desc": "Sow at 3-5cm depth with 45cm row spacing.", 
                "protocol": "Use Rhizobium-inoculated seeds. Ensure medium soil moisture.",
                "risk": "Soil-borne fungal rot in excessive moisture.",
                "daily_routine": ["Check germination percentage", "Monitor row moisture", "Look for early damping-off"]
            },
            {
                "start_day": 40, "end_day": 60, "title": "Flowering", 
                "desc": "Peak nutrient and water demand. Ensure no stress.", 
                "protocol": "Maintain soil moisture. Light weeding if necessary.",
                "risk": "Girdle beetle infestation can cause major damage.",
                "daily_routine": ["Inspect for girdle beetle damage", "Monitor bloom health", "Ensure irrigation if dry"]
            }
        ],
        "post_harvest": {
            "storage": "Dry to 10% moisture. Store in dry, ventilated bags to avoid rancidity.",
            "cleaning": "Remove stones and weed seeds before storage.",
            "soil_prep": "Excellent nitrogen restorer for the next wheat crop.",
            "residue": "Bhoosa (straw) is a rich protein source for cattle."
        }
    },
    {
        "name": "Groundnut",
        "category": "Oilseed",
        "image": "/crops/Groundnut.jpg",
        "growing_season": "Kharif",
        "avg_duration": "100-120 Days",
        "soil_preference": "Loose Sandy Loam",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Deep plowing to create loose soil for pod expansion. Apply Gypsum at pegging stage.",
            "irrigation_guidance": "Pre-sowing irrigation is beneficial. Flowering and pegging are critical stages.",
            "fertilizer_practices": "Higher requirement for Calcium and Sulfur. NPK (20:40:20) + Gypsum.",
            "seasonal_tips": "Do not stir soil once pegging starts to avoid damaging emerging pods."
        },
        "pests_diseases": [
            {
                "name": "Tikka Leaf Spot",
                "symptoms": "Circular dark spots on leaves with yellow halos.",
                "causes": "Cercospora fungus during humid weather.",
                "risk_stage": "Late Vegetative to Fruiting",
                "prevention": "Crop rotation and seed treatment with Thiram.",
                "treatment": "Foliar spray of Carbendazim or Mancozeb.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "Leaf Spot Warning",
                "msg": "Current humidity favors Tikka disease. Inspect lower leaves for spots."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 10, "title": "Establishment", 
                "desc": "Plant kernels at 5cm depth. Firm the soil properly.", 
                "protocol": "Use bold seeds for better vigor. Control soil grubs.",
                "risk": "White grub damage to germinating seeds.",
                "daily_routine": ["Check emergence vigor", "Watch for crow activity", "Moisture check"]
            },
            {
                "start_day": 45, "end_day": 60, "title": "Pegging Stage", 
                "desc": "Flower stalks enter the soil to form pods.", 
                "protocol": "Apply Gypsum. Ensure soil is loose and moist. Avoid weeding.",
                "risk": "Soil crusting preventing peg entry.",
                "daily_routine": ["Ensure peg soil contact", "Light irrigation if crusty", "Observation for grubs"]
            }
        ],
        "post_harvest": {
            "storage": "Sun-dry pods until they rattle. Store in moisture-proof containers.",
            "cleaning": "Separate earth and mud from harvested pods.",
            "soil_prep": "Prepare for winter mustard or gram.",
            "residue": "Groundnut haulm is premium quality hay for livestock."
        }
    },
    {
        "name": "Tobacco",
        "category": "Commercial",
        "image": "/crops/Tobacco.jpg",
        "growing_season": "Winter/Rabi",
        "avg_duration": "120-150 Days",
        "soil_preference": "Well-drained Sandy/Loam",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Requires very fine tilth and high organic fertility.",
            "irrigation_guidance": "Light, frequent irrigations. Avoid waterlogging at all stages.",
            "fertilizer_practices": "High Nitrogen requirement for leaf growth. Apply in split doses.",
            "seasonal_tips": "Desuckering and topping are critical for quality and nicotine content."
        },
        "pests_diseases": [
            {
                "name": "Tobacco Caterpillar",
                "symptoms": "Leaves are skeletonized by larvae feeding.",
                "causes": "Spodoptera litura feeding on the foliage.",
                "risk_stage": "Vegetative Growth",
                "prevention": "Pheromone traps and bird perches.",
                "treatment": "Spray Neem-based pesticides or Spinosad.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Biological",
                "title": "Aphid Incursion",
                "msg": "Mild weather predicted. Check lower leaf surface for green aphids."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 15, "title": "Transplanting", 
                "desc": "Transplant 6-8 week old seedlings into the main field.", 
                "protocol": "Space at 60x60cm. Irrigate immediately after transplanting.",
                "risk": "Cutworm attack on young transplants.",
                "daily_routine": ["Check for stem cutting", "Immediate gap filling", "Water at base"]
            },
            {
                "start_day": 60, "end_day": 90, "title": "Topping", 
                "desc": "Remove the flower head to direct energy to leaves.", 
                "protocol": "Snap off flower buds early. Follow with desuckering.",
                "risk": "Secondary suckers reduce leaf weight and quality.",
                "daily_routine": ["Snap flower heads", "Apply sucker oil", "Inspect for mosaic virus"]
            }
        ],
        "post_harvest": {
            "storage": "Cure leaves (Air/Flue) until desired color and aroma are reached.",
            "cleaning": "Remove dust and debris from cured leaves.",
            "soil_prep": "Follow with a green manure crop.",
            "residue": "Stalks can be used for making natural pesticides."
        }
    },
    {
        "name": "Watermelon",
        "category": "Fruit",
        "image": "/crops/watermelon.jpg",
        "growing_season": "Summer",
        "avg_duration": "80-90 Days",
        "soil_preference": "Deep Sandy Loam",
        "water_requirement": "Moderate",
        "cultivation_guide": {
            "soil_preparation": "Best grown in riverbeds or well-drained sandy soil. Prepare mounds or ridges.",
            "irrigation_guidance": "Critical water stages are flowering and fruit setting. Reduce water during ripening.",
            "fertilizer_practices": "Apply balanced NPK. High Boron and Micronutrients for sweetness and fruit health.",
            "seasonal_tips": "Hand pollination can improve fruit set in early stages."
        },
        "pests_diseases": [
            {
                "name": "Fruit Fly",
                "symptoms": "Punctures on fruits with rotting on the inside.",
                "causes": "Female flies laying eggs inside ripening fruit.",
                "risk_stage": "Fruit Setting to Ripening",
                "prevention": "Use pheromone traps and cover small fruits with paper bags.",
                "treatment": "Spray Malathion or use poisoned bait traps.",
                "risk_level": "High"
            }
        ],
        "active_alerts": [
            {
                "type": "Weather",
                "title": "Intense Heat Warning",
                "msg": "Temperatures above 42°C. Ensure mulching to prevent fruit sunscald."
            }
        ],
        "routine": [
            {
                "start_day": 1, "end_day": 10, "title": "Sowing", 
                "desc": "Direct sowing on hills or ridges with 3.0m spacing.", 
                "protocol": "Sow 2-3 seeds per pit. Thin to one healthy plant later.",
                "risk": "Poor emergence in crusty or heavy soils.",
                "daily_routine": ["Monitor emergence", "Check ridge stability", "Light hydration"]
            },
            {
                "start_day": 40, "end_day": 60, "title": "Fruit Set", 
                "desc": "Pollination and early fruit expansion.", 
                "protocol": "Ensure high bee activity. Watch for fruit-fly punctures.",
                "risk": "Fruit fly damage leads to rapid rot.",
                "daily_routine": ["Count healthy fruits", "Check pheromone traps", "Place fruits on dry mulch"]
            }
        ],
        "post_harvest": {
            "storage": "Harvest when the tendril withers and the 'thump' sound is dull.",
            "cleaning": "Wipe fruits to remove soil; grade by weight.",
            "soil_prep": "Prepare for Kharif corn or pulses.",
            "residue": "Healthy vines can be used as green manure."
        }
    }
]

# Soil/Season Compatibility Mapping
SUITABILITY_DATA = [
    {"soil": "Alluvial", "season": "Summer", "climate": "Hot", "crops": ["Rice", "Sugarcane", "Watermelon", "Banana"]},
    {"soil": "Alluvial", "season": "Summer", "climate": "Moderate", "crops": ["Rice", "Banana", "Tomato"]},
    {"soil": "Alluvial", "season": "Kharif", "climate": "Moderate", "crops": ["Rice", "Maize", "Soybean", "Groundnut"]},
    {"soil": "Alluvial", "season": "Winter", "climate": "Cool", "crops": ["Wheat", "Mustard", "Potato", "Tobacco"]},
    {"soil": "Red", "season": "Kharif", "climate": "Moderate", "crops": ["Groundnut", "Maize", "Tomato", "Soybean"]},
    {"soil": "Black", "season": "Summer", "climate": "Hot", "crops": ["Cotton", "Soybean", "Sugarcane", "Banana"]}
]

# Enriched Market Data (Crop Market)
MARKET_DATA = [
    {"product": "Rice (Basmati)", "price": "₹42,000/ton", "trend": "+3.4%", "stock": "High", "category": "Commodities", "desc": "Premium long-grain basmati rice. Export quality."},
    {"product": "Wheat (Sharbati)", "price": "₹28,500/ton", "trend": "+1.2%", "stock": "Moderate", "category": "Commodities", "desc": "Superior quality wheat known for its taste and shine."},
    {"product": "Soybean (Non-GMO)", "price": "₹48,900/ton", "trend": "+0.5%", "stock": "Moderate", "category": "Commodities", "desc": "Pure non-GMO soybean with high protein content."},
    {"product": "Sugarcane (Juicy)", "price": "₹3,200/ton", "trend": "+2.8%", "stock": "High", "category": "Commodities", "desc": "High-sucrose sugarcane for milling and juice production."},
    {"product": "Potato (Cold Storage)", "price": "₹15,400/ton", "trend": "+4.1%", "stock": "Low", "category": "Commodities", "desc": "High-quality table potatoes stored under controlled temperatures."},
    {"product": "Tomato (Hybrid)", "price": "₹22,000/ton", "trend": "-5.2%", "stock": "Very High", "category": "Commodities", "desc": "Firm hybrid tomatoes ideal for long-distance transport."},
    {"product": "Mustard (High Oil)", "price": "₹54,200/ton", "trend": "+0.8%", "stock": "Moderate", "category": "Commodities", "desc": "Premium mustard seeds with oil content exceeding 42%."},
    {"product": "Banana (Grand Naine)", "price": "₹12,500/ton", "trend": "+1.5%", "stock": "Moderate", "category": "Fruit", "desc": "Uniform premium quality Cavendish bananas for export."},
    {"product": "Watermelon (Sugar Baby)", "price": "₹8,000/ton", "trend": "-2.1%", "stock": "High", "category": "Fruit", "desc": "Sweet, dark-green watermelon with high TSS content."},
    {"product": "Tobacco (Virginia)", "price": "₹1,85,000/ton", "trend": "+4.5%", "stock": "Low", "category": "Commodities", "desc": "Flue-cured Virginia tobacco with bright leaf color."},
]

# Informational Resource Marketplace Data
RESOURCE_MARKETPLACE_DATA = [
    # Seeds
    {
        "product": "Hybrid Rice Seeds (IR-64)", 
        "category": "Seeds",
        "suitable_crops": ["Rice"],
        "usage_stage": "Nursery Preparation",
        "price_range": "₹400 - ₹500 per kg",
        "guidance": "Sow in prepared nursery beds. Ensure soil is moist and well-drained.",
        "availability": "In Stock (Nationwide)",
        "desc": "High-yielding rice seeds, pest resistant and drought tolerant."
    },
    {
        "product": "Bt-Cotton Elite Seeds", 
        "category": "Seeds",
        "suitable_crops": ["Cotton"],
        "usage_stage": "Sowing",
        "price_range": "₹900 - ₹1100 per pack",
        "guidance": "Plant in deep, well-aerated soil. Treat with recommended fungicides before sowing.",
        "availability": "Limited Stock (Regional)",
        "desc": "Genetically modified cotton seeds resistant to bollworms."
    },
    {
        "product": "Durum Wheat Seeds (Unnat)", 
        "category": "Seeds",
        "suitable_crops": ["Wheat"],
        "usage_stage": "Sowing",
        "price_range": "₹1100 - ₹1300 per 50kg",
        "guidance": "Best sown during mid-November. Use seed drill for uniform spacing.",
        "availability": "Available for Pre-order",
        "desc": "Hard wheat varieties ideal for pasta and semolina."
    },
    
    # Fertilizers
    {
        "product": "Urea (46% Nitrogen)", 
        "category": "Fertilizers",
        "suitable_crops": ["All Crops"],
        "usage_stage": "Vegetative Growth",
        "price_range": "₹260 - ₹280 per 45kg",
        "guidance": "Apply in splits. Best when soil has adequate moisture. Avoid heavy rain application.",
        "availability": "Subsidized (Govt Centers)",
        "desc": "Most widely used nitrogenous fertilizer for rapid growth."
    },
    {
        "product": "DAP (Diammonium Phosphate)", 
        "category": "Fertilizers",
        "suitable_crops": ["Maize", "Wheat", "Potato"],
        "usage_stage": "Sowing / Basal Dose",
        "price_range": "₹1300 - ₹1400 per 50kg",
        "guidance": "High phosphorus content. Incorporate into soil before or during sowing.",
        "availability": "In Stock",
        "desc": "Concentrated phosphorus fertilizer for root development."
    },

    # Pesticides
    {
        "product": "Chlorpyriphos 20% EC", 
        "category": "Pesticides",
        "suitable_crops": ["Wheat", "Sugarcane", "Rice"],
        "usage_stage": "Early Growth / Infestation",
        "price_range": "₹350 - ₹450 per liter",
        "guidance": "Effective against termites and stem borers. Follow safety label strictly.",
        "availability": "Available at Local Dealers",
        "desc": "Broad-spectrum insecticide for soil-borne and foliar pests."
    },
    {
        "product": "Imidacloprid 17.8% SL", 
        "category": "Pesticides",
        "suitable_crops": ["Cotton", "Chili", "Tomato"],
        "usage_stage": "Fruition / Vegetative",
        "price_range": "₹800 - ₹950 per 500ml",
        "guidance": "Systemic insecticide for sucking pests like Aphids and Thrips. Spray in early morning.",
        "availability": "High Demand",
        "desc": "Effective control for complex sucking pest attacks."
    },

    # Equipment
    {
        "product": "John Deere 5310 Tractor", 
        "category": "Equipments",
        "suitable_crops": ["Multi-purpose"],
        "usage_stage": "Land Prep / Harvest",
        "price_range": "₹8,50,000 - ₹9,20,000",
        "guidance": "Powerful 55HP engine. Ideal for heavy-duty plowing and trolley operations.",
        "availability": "Showroom Display Only",
        "desc": "Premium heavy-duty tractor with advanced agricultural technology."
    },
    {
        "product": "Laser Land Leveler (RTX)", 
        "category": "Equipments",
        "suitable_crops": ["Rice", "Wheat"],
        "usage_stage": "Pre-sowing",
        "price_range": "₹3,20,000 - ₹3,60,000",
        "guidance": "Saves 30% water and 25% fertilizer by ensuring uniform land surface.",
        "availability": "On-demand Booking",
        "desc": "Precision land leveling tool for modern water-efficient farming."
    },
    {
        "product": "NPK 19:19:19 (Water Soluble)", 
        "category": "Fertilizers",
        "suitable_crops": ["Tomato", "Chili", "Banana"],
        "usage_stage": "Vegetative to Fruiting",
        "price_range": "₹150 - ₹180 per kg",
        "guidance": "Ideal for fertigation. Provides balanced nutrients for overall plant development.",
        "availability": "Available Online",
        "desc": "Premium grade 100% water-soluble fertilizer for high-value crops."
    },
    {
        "product": "Organic Neem Oil (1500 ppm)", 
        "category": "Pesticides",
        "suitable_crops": ["Mustard", "Tomato", "Rice"],
        "usage_stage": "Preventative / Infestation",
        "price_range": "₹450 - ₹550 per liter",
        "guidance": "Eco-friendly pest control. Effective against wide range of sucking and chewing pests.",
        "availability": "High Stock",
        "desc": "Pure, cold-pressed neem oil for sustainable and organic farming."
    },
    {
        "product": "Solar Pump Subsidy Guide", 
        "category": "Resources",
        "suitable_crops": ["All Crops"],
        "usage_stage": "Planning",
        "price_range": "Free (Provided by Govt)",
        "guidance": "Step-by-step application manual for PM-KUSUM scheme benefits.",
        "availability": "Downloadable PDF",
        "desc": "Comprehensive guide to government subsidies for solar-powered irrigation."
    },
    {
        "product": "Drip Irrigation Manual", 
        "category": "Equipments",
        "suitable_crops": ["Sugarcane", "Tomato", "Cotton"],
        "usage_stage": "Pre-planting",
        "price_range": "Free with Installation",
        "guidance": "Technical manual for maintenance and operation of drip irrigation systems.",
        "availability": "Physical Copy / Digital",
        "desc": "Expert guidance on maximizing water efficiency with drip tech."
    },
    {
        "product": "Organic Certification Guide", 
        "category": "Resources",
        "suitable_crops": ["All Crops"],
        "usage_stage": "Annual Planning",
        "price_range": "₹500 for Certification Kit",
        "guidance": "Everything you need to know about NPOP certification process in India.",
        "availability": "Limited Edition",
        "desc": "Unlock premium markets by getting your farm organically certified."
    }
]

def seed_users():
    # Only seed if admin doesn't exist to avoid password re-hashing or duplicates
    if not db.users.find_one({"role": "admin"}):
        admin_data = {
            "email": "admin@agroassist.com",
            "password": bcrypt.generate_password_hash("admin123").decode('utf-8'),
            "fullname": "AgroAssist Admin",
            "role": "admin"
        }
        db.users.insert_one(admin_data)
        print("Seeded default administrator account (Email: admin@agroassist.com, Pass: admin123).")
    else:
        print("Admin account already exists. Skipping user seed.")

def seed_data():
    db.crops.delete_many({})
    db.crops.insert_many(CROP_ROUTINES_DATA)
    print(f"Seeded {len(CROP_ROUTINES_DATA)} crops.")

    db.suitability.delete_many({})
    db.suitability.insert_many(SUITABILITY_DATA)
    print(f"Seeded {len(SUITABILITY_DATA)} suitability rules.")

    db.market.delete_many({})
    db.market.insert_many(MARKET_DATA)
    print(f"Seeded {len(MARKET_DATA)} market items.")

    db.resources.delete_many({})
    db.resources.insert_many(RESOURCE_MARKETPLACE_DATA)
    print(f"Seeded {len(RESOURCE_MARKETPLACE_DATA)} resource items.")

    seed_users()

    print("\n✅ Database migration and seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
