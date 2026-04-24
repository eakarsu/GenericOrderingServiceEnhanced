"""Seed data - at least 15 items per sector across all 19 sectors."""
from datetime import datetime, timedelta
import random
from .models import User, UserSettings, Sector, Category, Item, Order, OrderItem
from .auth_utils import hash_password


def seed_database(db):
    """Seed the database with comprehensive data for all features."""

    # Check if already seeded
    if db.query(User).count() > 0:
        print("Database already seeded, skipping...")
        return

    print("Seeding database...")

    # ===================== USERS (15+) =====================
    users_data = [
        {"username": "admin", "email": "admin@omniassist.com", "password": "Admin@123!", "first_name": "System", "last_name": "Admin", "role": "admin", "phone": "+1234567890", "is_verified": True},
        {"username": "manager1", "email": "manager1@omniassist.com", "password": "Manager@123!", "first_name": "Sarah", "last_name": "Johnson", "role": "manager", "phone": "+1234567891", "is_verified": True},
        {"username": "manager2", "email": "manager2@omniassist.com", "password": "Manager@123!", "first_name": "Mike", "last_name": "Williams", "role": "manager", "phone": "+1234567892", "is_verified": True},
        {"username": "john_doe", "email": "john@example.com", "password": "User@1234!", "first_name": "John", "last_name": "Doe", "role": "user", "phone": "+1555000001", "is_verified": True},
        {"username": "jane_smith", "email": "jane@example.com", "password": "User@1234!", "first_name": "Jane", "last_name": "Smith", "role": "user", "phone": "+1555000002", "is_verified": True},
        {"username": "bob_wilson", "email": "bob@example.com", "password": "User@1234!", "first_name": "Bob", "last_name": "Wilson", "role": "user", "phone": "+1555000003", "is_verified": True},
        {"username": "alice_brown", "email": "alice@example.com", "password": "User@1234!", "first_name": "Alice", "last_name": "Brown", "role": "user", "phone": "+1555000004", "is_verified": True},
        {"username": "charlie_davis", "email": "charlie@example.com", "password": "User@1234!", "first_name": "Charlie", "last_name": "Davis", "role": "user", "phone": "+1555000005", "is_verified": True},
        {"username": "diana_miller", "email": "diana@example.com", "password": "User@1234!", "first_name": "Diana", "last_name": "Miller", "role": "user", "phone": "+1555000006", "is_verified": True},
        {"username": "evan_garcia", "email": "evan@example.com", "password": "User@1234!", "first_name": "Evan", "last_name": "Garcia", "role": "user", "phone": "+1555000007", "is_verified": False},
        {"username": "fiona_lee", "email": "fiona@example.com", "password": "User@1234!", "first_name": "Fiona", "last_name": "Lee", "role": "user", "phone": "+1555000008", "is_verified": True},
        {"username": "george_taylor", "email": "george@example.com", "password": "User@1234!", "first_name": "George", "last_name": "Taylor", "role": "user", "phone": "+1555000009", "is_verified": True},
        {"username": "hannah_white", "email": "hannah@example.com", "password": "User@1234!", "first_name": "Hannah", "last_name": "White", "role": "viewer", "phone": "+1555000010", "is_verified": True},
        {"username": "ivan_martinez", "email": "ivan@example.com", "password": "User@1234!", "first_name": "Ivan", "last_name": "Martinez", "role": "viewer", "phone": "+1555000011", "is_verified": False},
        {"username": "julia_anderson", "email": "julia@example.com", "password": "User@1234!", "first_name": "Julia", "last_name": "Anderson", "role": "user", "phone": "+1555000012", "is_verified": True},
        {"username": "kevin_thomas", "email": "kevin@example.com", "password": "User@1234!", "first_name": "Kevin", "last_name": "Thomas", "role": "user", "phone": "+1555000013", "is_verified": True},
        {"username": "laura_jackson", "email": "laura@example.com", "password": "User@1234!", "first_name": "Laura", "last_name": "Jackson", "role": "user", "phone": "+1555000014", "is_verified": True},
    ]

    users = []
    for ud in users_data:
        user = User(
            username=ud["username"], email=ud["email"],
            password_hash=hash_password(ud["password"]),
            first_name=ud["first_name"], last_name=ud["last_name"],
            role=ud["role"], phone=ud["phone"],
            is_verified=ud["is_verified"], is_active=True
        )
        db.add(user)
        users.append(user)
    db.flush()

    # User settings
    for user in users:
        settings = UserSettings(
            user_id=user.id,
            theme=random.choice(["light", "dark"]),
            notifications_enabled=random.choice([True, False]),
            language="en",
            timezone=random.choice(["UTC", "US/Eastern", "US/Pacific", "Europe/London"]),
            items_per_page=random.choice([10, 15, 20, 25])
        )
        db.add(settings)

    # ===================== SECTORS & ITEMS =====================
    sectors_data = {
        "Food Delivery": {
            "slug": "food_delivery", "icon": "utensils", "color": "#EF4444",
            "description": "Order food from local restaurants - pizza, sushi, burgers, healthy meals and more",
            "categories": {
                "Breakfast": [
                    ("Classic Pancakes", "Fluffy buttermilk pancakes with maple syrup", 8.99, "breakfast,popular"),
                    ("Eggs Benedict", "Poached eggs on English muffin with hollandaise", 12.99, "breakfast,eggs"),
                    ("Avocado Toast", "Sourdough with smashed avocado and poached egg", 11.49, "breakfast,healthy"),
                    ("French Toast", "Brioche French toast with berries and cream", 10.99, "breakfast,sweet"),
                    ("Breakfast Burrito", "Scrambled eggs, cheese, beans, salsa in flour tortilla", 9.99, "breakfast,mexican"),
                ],
                "Lunch": [
                    ("Caesar Salad", "Romaine, parmesan, croutons, Caesar dressing", 10.99, "lunch,salad,healthy"),
                    ("Club Sandwich", "Triple-decker with turkey, bacon, lettuce, tomato", 12.49, "lunch,sandwich"),
                    ("Margherita Pizza", "Fresh mozzarella, tomato, basil on thin crust", 14.99, "lunch,pizza,italian"),
                    ("Chicken Wrap", "Grilled chicken, veggies, ranch in spinach wrap", 11.99, "lunch,wrap,healthy"),
                    ("Burger Deluxe", "Angus beef patty, cheddar, lettuce, tomato, fries", 15.99, "lunch,burger"),
                ],
                "Dinner": [
                    ("Grilled Salmon", "Atlantic salmon with lemon dill sauce and rice", 22.99, "dinner,seafood,healthy"),
                    ("Chicken Parmesan", "Breaded chicken, marinara, melted mozzarella, pasta", 18.99, "dinner,italian"),
                    ("Steak Frites", "8oz NY strip with garlic butter and hand-cut fries", 26.99, "dinner,steak"),
                    ("Pad Thai", "Rice noodles, shrimp, peanuts, bean sprouts", 16.99, "dinner,thai,asian"),
                    ("Vegetable Curry", "Mixed vegetables in coconut curry with basmati rice", 14.99, "dinner,vegetarian,indian"),
                ],
            }
        },
        "Auto Repair": {
            "slug": "auto_repair", "icon": "car", "color": "#3B82F6",
            "description": "Professional auto repair and maintenance services for all vehicle types",
            "categories": {
                "Oil & Fluids": [
                    ("Conventional Oil Change", "Up to 5 quarts conventional oil + filter", 39.99, "oil,basic,maintenance"),
                    ("Synthetic Oil Change", "Up to 5 quarts full synthetic oil + filter", 69.99, "oil,synthetic,maintenance"),
                    ("Transmission Fluid Flush", "Complete transmission fluid exchange", 149.99, "fluid,transmission"),
                    ("Coolant Flush", "Full cooling system flush and refill", 99.99, "fluid,coolant"),
                    ("Brake Fluid Change", "DOT 4 brake fluid replacement", 79.99, "fluid,brakes"),
                ],
                "Brakes": [
                    ("Front Brake Pad Replacement", "Premium ceramic pads for front axle", 189.99, "brakes,pads,front"),
                    ("Rear Brake Pad Replacement", "Premium ceramic pads for rear axle", 169.99, "brakes,pads,rear"),
                    ("Brake Rotor Resurfacing", "Machine resurface per rotor", 49.99, "brakes,rotor"),
                    ("Full Brake Service", "Pads, rotors, fluid for all four wheels", 499.99, "brakes,complete"),
                    ("Brake Caliper Replacement", "Single caliper replacement with hardware", 249.99, "brakes,caliper"),
                ],
                "Engine": [
                    ("Spark Plug Replacement", "Replace all spark plugs (4-cylinder)", 129.99, "engine,spark,tune-up"),
                    ("Timing Belt Replacement", "Timing belt and tensioner replacement", 599.99, "engine,timing,belt"),
                    ("Engine Diagnostic", "Full computer diagnostic scan", 89.99, "engine,diagnostic"),
                    ("Air Filter Replacement", "Engine and cabin air filter replacement", 49.99, "engine,filter"),
                    ("Battery Replacement", "New battery with installation and testing", 159.99, "engine,battery,electrical"),
                ],
            }
        },
        "Beauty Salon": {
            "slug": "beauty_salon", "icon": "scissors", "color": "#EC4899",
            "description": "Premium beauty services including haircuts, coloring, facials, and nail care",
            "categories": {
                "Hair Services": [
                    ("Women's Haircut & Style", "Precision cut with shampoo and blowout", 65.00, "hair,cut,women"),
                    ("Men's Haircut", "Classic or modern cut with styling", 35.00, "hair,cut,men"),
                    ("Full Color", "Single-process all-over color", 120.00, "hair,color"),
                    ("Highlights (Partial)", "Face-framing foil highlights", 95.00, "hair,highlights"),
                    ("Balayage", "Hand-painted highlights for natural look", 180.00, "hair,balayage,color"),
                ],
                "Nail Services": [
                    ("Classic Manicure", "Nail shaping, cuticle care, polish", 25.00, "nails,manicure"),
                    ("Gel Manicure", "Long-lasting gel polish application", 40.00, "nails,gel,manicure"),
                    ("Classic Pedicure", "Foot soak, exfoliation, nail care, polish", 35.00, "nails,pedicure"),
                    ("Spa Pedicure", "Deluxe pedicure with paraffin and massage", 55.00, "nails,spa,pedicure"),
                    ("Acrylic Full Set", "Full set of acrylic nail extensions", 60.00, "nails,acrylic"),
                ],
                "Skin Care": [
                    ("Express Facial", "30-minute cleansing and hydrating facial", 50.00, "skin,facial,express"),
                    ("Deep Cleansing Facial", "60-minute deep pore cleansing treatment", 85.00, "skin,facial,deep"),
                    ("Anti-Aging Facial", "Firming and rejuvenating facial treatment", 110.00, "skin,facial,anti-aging"),
                    ("Eyebrow Wax", "Precision eyebrow shaping with wax", 18.00, "skin,wax,eyebrow"),
                    ("Full Face Wax", "Complete facial hair removal", 45.00, "skin,wax,face"),
                ],
            }
        },
        "Healthcare": {
            "slug": "healthcare", "icon": "heart-pulse", "color": "#10B981",
            "description": "Medical appointments, consultations, lab tests, and telehealth services",
            "categories": {
                "Consultations": [
                    ("General Checkup", "Annual physical examination", 150.00, "consultation,general,checkup"),
                    ("Specialist Consultation", "Referral specialist visit", 250.00, "consultation,specialist"),
                    ("Telehealth Visit", "Video consultation with physician", 75.00, "consultation,telehealth,virtual"),
                    ("Urgent Care Visit", "Walk-in urgent care appointment", 125.00, "consultation,urgent"),
                    ("Pediatric Visit", "Child wellness check or sick visit", 120.00, "consultation,pediatric,children"),
                ],
                "Lab Tests": [
                    ("Complete Blood Count", "CBC with differential", 45.00, "lab,blood,cbc"),
                    ("Metabolic Panel", "Comprehensive metabolic panel", 65.00, "lab,blood,metabolic"),
                    ("Lipid Panel", "Cholesterol and triglyceride testing", 55.00, "lab,blood,lipid"),
                    ("Thyroid Panel", "TSH, T3, T4 testing", 75.00, "lab,blood,thyroid"),
                    ("Urinalysis", "Complete urine analysis", 30.00, "lab,urine"),
                ],
                "Wellness": [
                    ("Flu Vaccination", "Annual influenza vaccine", 35.00, "wellness,vaccine,flu"),
                    ("COVID-19 Test", "PCR test with results in 24 hours", 50.00, "wellness,test,covid"),
                    ("Allergy Testing", "Comprehensive allergy panel", 200.00, "wellness,allergy,test"),
                    ("Vision Screening", "Basic eye examination", 80.00, "wellness,vision,eye"),
                    ("Dental Cleaning", "Professional teeth cleaning and exam", 120.00, "wellness,dental,cleaning"),
                ],
            }
        },
        "Fitness Gym": {
            "slug": "fitness_gym", "icon": "dumbbell", "color": "#F59E0B",
            "description": "Gym memberships, personal training, group classes, and fitness programs",
            "categories": {
                "Memberships": [
                    ("Monthly Basic", "Access to gym floor and cardio equipment", 29.99, "membership,basic,monthly"),
                    ("Monthly Premium", "Full access including pool and sauna", 49.99, "membership,premium,monthly"),
                    ("Annual Basic", "12-month basic membership (save 20%)", 287.00, "membership,basic,annual"),
                    ("Annual Premium", "12-month premium membership (save 20%)", 479.00, "membership,premium,annual"),
                    ("Day Pass", "Single day full gym access", 15.00, "membership,day,pass"),
                ],
                "Personal Training": [
                    ("Single PT Session", "60-minute one-on-one training session", 70.00, "training,personal,single"),
                    ("5-Session PT Pack", "Five 60-minute personal training sessions", 325.00, "training,personal,pack"),
                    ("10-Session PT Pack", "Ten 60-minute personal training sessions", 600.00, "training,personal,pack"),
                    ("Nutrition Consultation", "Personalized meal plan with dietitian", 85.00, "training,nutrition"),
                    ("Body Composition Analysis", "InBody scan with detailed report", 40.00, "training,assessment"),
                ],
                "Group Classes": [
                    ("Yoga Class", "60-minute vinyasa flow yoga", 20.00, "class,yoga,flexibility"),
                    ("Spin Class", "45-minute high-intensity cycling", 22.00, "class,spin,cardio"),
                    ("CrossFit WOD", "60-minute CrossFit workout of the day", 25.00, "class,crossfit,strength"),
                    ("Pilates", "50-minute mat Pilates session", 20.00, "class,pilates,core"),
                    ("Boxing Fitness", "45-minute boxing cardio workout", 22.00, "class,boxing,cardio"),
                ],
            }
        },
        "Home Services": {
            "slug": "home_services", "icon": "house", "color": "#8B5CF6",
            "description": "Plumbing, electrical, HVAC, painting, cleaning, and general home repairs",
            "categories": {
                "Plumbing": [
                    ("Faucet Repair", "Fix dripping or leaking faucet", 89.99, "plumbing,faucet,repair"),
                    ("Drain Cleaning", "Professional drain unclogging service", 129.99, "plumbing,drain,cleaning"),
                    ("Toilet Repair", "Fix running or clogged toilet", 99.99, "plumbing,toilet,repair"),
                    ("Water Heater Service", "Water heater inspection and repair", 199.99, "plumbing,heater,repair"),
                    ("Pipe Leak Repair", "Locate and fix pipe leaks", 149.99, "plumbing,pipe,leak"),
                ],
                "Electrical": [
                    ("Outlet Installation", "Install new electrical outlet", 119.99, "electrical,outlet,install"),
                    ("Light Fixture Install", "Mount and wire new light fixture", 99.99, "electrical,light,install"),
                    ("Panel Upgrade", "Electrical panel upgrade to 200A", 1499.99, "electrical,panel,upgrade"),
                    ("Ceiling Fan Install", "Install ceiling fan with wiring", 159.99, "electrical,fan,install"),
                    ("Smart Home Wiring", "Smart switch/thermostat installation", 129.99, "electrical,smart,install"),
                ],
                "Cleaning": [
                    ("Standard Cleaning", "Regular cleaning for 2-bed apartment", 120.00, "cleaning,standard,apartment"),
                    ("Deep Cleaning", "Thorough deep cleaning for 2-bed apartment", 220.00, "cleaning,deep,apartment"),
                    ("Move-Out Cleaning", "Complete cleaning for move-out", 300.00, "cleaning,moveout"),
                    ("Carpet Cleaning", "Professional carpet cleaning per room", 75.00, "cleaning,carpet"),
                    ("Window Cleaning", "Interior/exterior window cleaning", 150.00, "cleaning,window"),
                ],
            }
        },
        "Pet Services": {
            "slug": "pet_services", "icon": "paw-print", "color": "#F97316",
            "description": "Pet grooming, veterinary care, boarding, dog walking, and pet supplies",
            "categories": {
                "Grooming": [
                    ("Dog Bath & Brush", "Shampoo, brush, and blow-dry", 35.00, "grooming,bath,dog"),
                    ("Full Dog Grooming", "Bath, haircut, nails, ears cleaning", 65.00, "grooming,full,dog"),
                    ("Cat Grooming", "Gentle cat bath and brush", 50.00, "grooming,bath,cat"),
                    ("Nail Trimming", "Nail trim for dogs or cats", 15.00, "grooming,nails"),
                    ("De-Shedding Treatment", "Specialized de-shedding service", 45.00, "grooming,deshed"),
                ],
                "Veterinary": [
                    ("Wellness Exam", "Comprehensive pet health checkup", 60.00, "vet,exam,wellness"),
                    ("Vaccination Package", "Core vaccines for dogs/cats", 95.00, "vet,vaccine"),
                    ("Dental Cleaning", "Professional pet dental cleaning", 250.00, "vet,dental"),
                    ("Spay/Neuter", "Surgical spay or neuter procedure", 200.00, "vet,surgery,spay"),
                    ("Microchipping", "Pet microchip implantation", 45.00, "vet,microchip"),
                ],
                "Boarding & Walking": [
                    ("Dog Walking (30 min)", "30-minute neighborhood walk", 20.00, "walking,dog,30min"),
                    ("Dog Walking (60 min)", "60-minute extended walk", 35.00, "walking,dog,60min"),
                    ("Overnight Boarding", "Per night pet boarding with care", 45.00, "boarding,overnight"),
                    ("Doggy Daycare", "Full day supervised play and care", 35.00, "boarding,daycare"),
                    ("Pet Sitting (In-Home)", "In-home pet sitting per visit", 30.00, "sitting,inhome"),
                ],
            }
        },
        "Education Tutoring": {
            "slug": "education_tutoring", "icon": "graduation-cap", "color": "#06B6D4",
            "description": "Academic tutoring, test prep, language learning, and professional development",
            "categories": {
                "Academic Tutoring": [
                    ("Math Tutoring (1hr)", "One-on-one math tutoring session", 50.00, "tutoring,math,academic"),
                    ("Science Tutoring (1hr)", "Physics, chemistry, biology tutoring", 55.00, "tutoring,science,academic"),
                    ("English/Writing (1hr)", "Reading comprehension and essay writing", 45.00, "tutoring,english,writing"),
                    ("History Tutoring (1hr)", "History and social studies help", 45.00, "tutoring,history,academic"),
                    ("Computer Science (1hr)", "Programming and CS fundamentals", 60.00, "tutoring,cs,programming"),
                ],
                "Test Prep": [
                    ("SAT Prep Course", "8-week comprehensive SAT preparation", 599.00, "testprep,sat,course"),
                    ("ACT Prep Course", "8-week comprehensive ACT preparation", 599.00, "testprep,act,course"),
                    ("GRE Prep Session", "Individual GRE prep tutoring", 75.00, "testprep,gre,session"),
                    ("GMAT Prep Session", "Individual GMAT prep tutoring", 80.00, "testprep,gmat,session"),
                    ("TOEFL Prep Session", "TOEFL preparation and practice", 60.00, "testprep,toefl,language"),
                ],
                "Languages": [
                    ("Spanish Lesson (1hr)", "Conversational Spanish tutoring", 40.00, "language,spanish"),
                    ("French Lesson (1hr)", "French language tutoring", 45.00, "language,french"),
                    ("Mandarin Lesson (1hr)", "Mandarin Chinese tutoring", 55.00, "language,mandarin,chinese"),
                    ("ESL Lesson (1hr)", "English as second language tutoring", 40.00, "language,esl,english"),
                    ("Japanese Lesson (1hr)", "Japanese language tutoring", 50.00, "language,japanese"),
                ],
            }
        },
        "Event Planning": {
            "slug": "event_planning", "icon": "calendar-days", "color": "#A855F7",
            "description": "Wedding planning, corporate events, birthday parties, and special occasions",
            "categories": {
                "Weddings": [
                    ("Full Wedding Planning", "Complete wedding coordination package", 5000.00, "wedding,full,planning"),
                    ("Day-Of Coordination", "Wedding day management and coordination", 1500.00, "wedding,dayof,coordination"),
                    ("Wedding Floral Package", "Bridal bouquet, centerpieces, ceremony flowers", 2500.00, "wedding,floral,flowers"),
                    ("Wedding DJ Package", "DJ, MC, sound system for 6 hours", 1200.00, "wedding,dj,music"),
                    ("Wedding Photography", "8-hour coverage, edited digital gallery", 3000.00, "wedding,photo,photography"),
                ],
                "Corporate Events": [
                    ("Conference Planning", "Full conference organization for 100+ people", 8000.00, "corporate,conference"),
                    ("Team Building Event", "Half-day team building activity coordination", 1500.00, "corporate,team,building"),
                    ("Holiday Party", "Corporate holiday party for 50 people", 3000.00, "corporate,holiday,party"),
                    ("Product Launch", "Product launch event planning and execution", 5000.00, "corporate,launch,product"),
                    ("Business Dinner", "Formal business dinner for 20 guests", 2000.00, "corporate,dinner"),
                ],
                "Private Parties": [
                    ("Birthday Party Package", "Decorations, cake, entertainment for 20", 500.00, "party,birthday"),
                    ("Kids Party Package", "Themed party with games for 15 children", 400.00, "party,kids,themed"),
                    ("Cocktail Party", "Bartender, apps, setup for 30 guests", 800.00, "party,cocktail"),
                    ("Anniversary Celebration", "Elegant anniversary dinner for 40", 1500.00, "party,anniversary"),
                    ("Graduation Party", "Outdoor graduation celebration for 50", 700.00, "party,graduation"),
                ],
            }
        },
        "Financial Services": {
            "slug": "financial_services", "icon": "landmark", "color": "#059669",
            "description": "Banking, investments, tax preparation, financial planning, and insurance",
            "categories": {
                "Banking": [
                    ("Checking Account Setup", "New checking account with debit card", 0.00, "banking,checking,account"),
                    ("Savings Account Setup", "High-yield savings account opening", 0.00, "banking,savings,account"),
                    ("Wire Transfer", "Domestic wire transfer service", 25.00, "banking,wire,transfer"),
                    ("Cashier's Check", "Certified cashier's check issuance", 10.00, "banking,check,cashier"),
                    ("Safe Deposit Box (Annual)", "Small safe deposit box rental", 75.00, "banking,safe,deposit"),
                ],
                "Investments": [
                    ("Portfolio Review", "Comprehensive investment portfolio analysis", 150.00, "investment,portfolio,review"),
                    ("Financial Planning Session", "1-hour financial planning consultation", 200.00, "investment,planning,consultation"),
                    ("Retirement Planning", "401k/IRA strategy consultation", 175.00, "investment,retirement,planning"),
                    ("Stock Trading Account", "Brokerage account setup and orientation", 0.00, "investment,trading,stocks"),
                    ("Estate Planning Consult", "Estate planning strategy session", 300.00, "investment,estate,planning"),
                ],
                "Tax Services": [
                    ("Individual Tax Return", "Standard individual tax preparation", 200.00, "tax,individual,return"),
                    ("Business Tax Return", "Small business tax preparation", 500.00, "tax,business,return"),
                    ("Tax Planning Session", "Proactive tax strategy consultation", 150.00, "tax,planning,strategy"),
                    ("Tax Amendment", "Amended tax return filing", 100.00, "tax,amendment,return"),
                    ("Quarterly Estimated Taxes", "Quarterly tax estimate preparation", 75.00, "tax,quarterly,estimated"),
                ],
            }
        },
        "Insurance": {
            "slug": "insurance", "icon": "shield-check", "color": "#0EA5E9",
            "description": "Auto, home, life, health, and business insurance policies and claims",
            "categories": {
                "Auto Insurance": [
                    ("Basic Auto Policy", "Liability-only auto insurance", 89.00, "auto,basic,liability"),
                    ("Full Coverage Auto", "Comprehensive + collision coverage", 175.00, "auto,full,coverage"),
                    ("SR-22 Filing", "SR-22 certificate filing service", 25.00, "auto,sr22,filing"),
                    ("Roadside Assistance Add-on", "24/7 roadside assistance coverage", 12.00, "auto,roadside,addon"),
                    ("Rental Car Coverage", "Rental reimbursement add-on", 8.00, "auto,rental,addon"),
                ],
                "Home Insurance": [
                    ("Homeowners Policy", "Standard homeowners insurance", 125.00, "home,homeowners,policy"),
                    ("Renters Insurance", "Renters personal property coverage", 25.00, "home,renters,policy"),
                    ("Flood Insurance", "Flood damage coverage add-on", 45.00, "home,flood,addon"),
                    ("Umbrella Policy", "Additional liability umbrella coverage", 30.00, "home,umbrella,policy"),
                    ("Jewelry Rider", "Scheduled personal property for jewelry", 15.00, "home,jewelry,rider"),
                ],
                "Life & Health": [
                    ("Term Life 20-Year", "20-year term life insurance policy", 35.00, "life,term,20year"),
                    ("Whole Life Policy", "Permanent whole life insurance", 150.00, "life,whole,permanent"),
                    ("Health Insurance (Individual)", "Individual health coverage plan", 350.00, "health,individual"),
                    ("Dental Insurance", "Dental coverage plan", 35.00, "health,dental"),
                    ("Vision Insurance", "Vision coverage plan", 15.00, "health,vision"),
                ],
            }
        },
        "IT Services": {
            "slug": "it_services", "icon": "monitor", "color": "#6366F1",
            "description": "Tech support, software development, cloud services, and cybersecurity",
            "categories": {
                "Tech Support": [
                    ("PC Tune-Up", "System optimization and malware removal", 89.99, "support,tuneup,pc"),
                    ("Virus Removal", "Complete malware and virus removal", 129.99, "support,virus,malware"),
                    ("Data Recovery", "Hard drive data recovery service", 199.99, "support,data,recovery"),
                    ("Network Setup", "Home/office network configuration", 149.99, "support,network,setup"),
                    ("Email Setup", "Email client configuration and migration", 59.99, "support,email,setup"),
                ],
                "Development": [
                    ("Website Development", "Custom responsive website (5 pages)", 2500.00, "dev,website,custom"),
                    ("Mobile App MVP", "Cross-platform mobile app MVP", 5000.00, "dev,mobile,app"),
                    ("API Development", "RESTful API design and implementation", 3000.00, "dev,api,backend"),
                    ("Database Design", "Database schema design and optimization", 1500.00, "dev,database,design"),
                    ("WordPress Site", "Custom WordPress site with theme", 1200.00, "dev,wordpress,cms"),
                ],
                "Cloud & Security": [
                    ("Cloud Migration", "Migrate services to AWS/Azure/GCP", 3000.00, "cloud,migration,aws"),
                    ("Security Audit", "Comprehensive cybersecurity assessment", 2000.00, "security,audit,assessment"),
                    ("SSL Certificate Setup", "SSL/TLS certificate installation", 99.99, "security,ssl,certificate"),
                    ("Backup Solution", "Automated backup system setup", 299.99, "cloud,backup,solution"),
                    ("VPN Setup", "Corporate VPN configuration", 199.99, "security,vpn,setup"),
                ],
            }
        },
        "Legal Services": {
            "slug": "legal_services", "icon": "scale", "color": "#78716C",
            "description": "Legal consultation, document preparation, business formation, and litigation",
            "categories": {
                "Consultations": [
                    ("Initial Legal Consultation", "30-minute initial legal consultation", 100.00, "consultation,initial,legal"),
                    ("Contract Review", "Review and advise on legal contracts", 250.00, "consultation,contract,review"),
                    ("Legal Letter Drafting", "Professional legal letter preparation", 200.00, "consultation,letter,drafting"),
                    ("Demand Letter", "Formal demand letter to opposing party", 350.00, "consultation,demand,letter"),
                    ("Legal Research", "Targeted legal research and memo", 175.00, "consultation,research,memo"),
                ],
                "Business Law": [
                    ("LLC Formation", "LLC filing and operating agreement", 500.00, "business,llc,formation"),
                    ("Corporation Formation", "Corp filing, bylaws, and minutes", 750.00, "business,corporation,formation"),
                    ("Trademark Registration", "Federal trademark application", 600.00, "business,trademark,ip"),
                    ("Business License Help", "Business license application assistance", 200.00, "business,license,permit"),
                    ("Partnership Agreement", "Draft custom partnership agreement", 800.00, "business,partnership,agreement"),
                ],
                "Personal Law": [
                    ("Will Preparation", "Last will and testament drafting", 400.00, "personal,will,estate"),
                    ("Power of Attorney", "POA document preparation", 250.00, "personal,poa,power"),
                    ("Real Estate Closing", "Real estate closing representation", 1000.00, "personal,realestate,closing"),
                    ("Traffic Ticket Defense", "Traffic violation defense", 300.00, "personal,traffic,defense"),
                    ("Name Change Filing", "Legal name change petition", 350.00, "personal,namechange,filing"),
                ],
            }
        },
        "Transportation": {
            "slug": "transportation", "icon": "truck", "color": "#EA580C",
            "description": "Ride-sharing, taxi service, airport transfers, and charter transportation",
            "categories": {
                "Rides": [
                    ("Standard Ride (5 mi)", "Sedan ride up to 5 miles", 12.00, "ride,standard,sedan"),
                    ("Premium Ride (5 mi)", "Luxury vehicle ride up to 5 miles", 22.00, "ride,premium,luxury"),
                    ("XL Ride (5 mi)", "SUV/van ride for up to 6 passengers", 18.00, "ride,xl,suv"),
                    ("Shared Ride (5 mi)", "Shared pool ride up to 5 miles", 8.00, "ride,shared,pool"),
                    ("Hourly Chauffeur", "Dedicated driver for 1 hour", 55.00, "ride,chauffeur,hourly"),
                ],
                "Airport": [
                    ("Airport Pickup", "Airport arrival pickup service", 45.00, "airport,pickup,arrival"),
                    ("Airport Drop-off", "Airport departure drop-off", 40.00, "airport,dropoff,departure"),
                    ("Airport Round Trip", "Round trip airport transfer", 75.00, "airport,roundtrip,transfer"),
                    ("Meet & Greet Airport", "Meet at gate with sign service", 65.00, "airport,meet,greet"),
                    ("Airport Shuttle (per person)", "Shared airport shuttle service", 20.00, "airport,shuttle,shared"),
                ],
                "Charter": [
                    ("City Tour (3 hours)", "Guided city sightseeing tour", 150.00, "charter,tour,city"),
                    ("Wine Country Tour", "Full day wine country excursion", 350.00, "charter,tour,wine"),
                    ("Corporate Shuttle", "Employee shuttle service (daily)", 200.00, "charter,corporate,shuttle"),
                    ("Wedding Transportation", "Wedding party bus/limo service", 500.00, "charter,wedding,limo"),
                    ("Group Outing Bus", "Charter bus for 40+ passengers", 800.00, "charter,bus,group"),
                ],
            }
        },
        "Travel Hotel": {
            "slug": "travel_hotel", "icon": "plane", "color": "#0891B2",
            "description": "Hotel bookings, flight reservations, vacation packages, and travel planning",
            "categories": {
                "Hotels": [
                    ("Budget Room (per night)", "Standard room in 2-star hotel", 79.00, "hotel,budget,standard"),
                    ("Comfort Room (per night)", "Deluxe room in 3-star hotel", 129.00, "hotel,comfort,deluxe"),
                    ("Premium Room (per night)", "Superior room in 4-star hotel", 199.00, "hotel,premium,superior"),
                    ("Luxury Suite (per night)", "Suite in 5-star luxury hotel", 399.00, "hotel,luxury,suite"),
                    ("Boutique Hotel (per night)", "Unique boutique hotel experience", 179.00, "hotel,boutique,unique"),
                ],
                "Flights": [
                    ("Domestic Economy", "Round-trip domestic economy class", 299.00, "flight,domestic,economy"),
                    ("Domestic Business", "Round-trip domestic business class", 699.00, "flight,domestic,business"),
                    ("International Economy", "Round-trip international economy", 799.00, "flight,international,economy"),
                    ("International Business", "Round-trip international business class", 2500.00, "flight,international,business"),
                    ("First Class Upgrade", "Upgrade from economy to first class", 500.00, "flight,upgrade,first"),
                ],
                "Packages": [
                    ("Weekend Getaway", "2 nights hotel + breakfast", 299.00, "package,weekend,getaway"),
                    ("Beach Vacation (5 nights)", "5 nights beachfront resort all-inclusive", 1500.00, "package,beach,resort"),
                    ("City Break (3 nights)", "3 nights city center hotel + tours", 599.00, "package,city,break"),
                    ("Ski Package (4 nights)", "4 nights ski lodge + lift passes", 999.00, "package,ski,mountain"),
                    ("Honeymoon Package", "7 nights luxury romantic getaway", 3500.00, "package,honeymoon,romantic"),
                ],
            }
        },
        "Photography": {
            "slug": "photography", "icon": "camera", "color": "#D946EF",
            "description": "Professional photography for weddings, portraits, events, and commercial use",
            "categories": {
                "Portrait": [
                    ("Headshot Session", "Professional headshot - 30 min, 5 edited photos", 150.00, "portrait,headshot,professional"),
                    ("Family Portrait", "1-hour family session, 15 edited photos", 300.00, "portrait,family,session"),
                    ("Senior Portrait", "1-hour senior portrait, 20 edited photos", 250.00, "portrait,senior,session"),
                    ("Couples Session", "1-hour couples shoot, 20 edited photos", 275.00, "portrait,couples,romantic"),
                    ("Maternity Session", "1-hour maternity shoot, 15 edited photos", 275.00, "portrait,maternity,baby"),
                ],
                "Events": [
                    ("Wedding Photography (8hr)", "Full wedding day coverage, 400+ photos", 3000.00, "event,wedding,fullday"),
                    ("Engagement Session", "1-hour engagement shoot, 30 photos", 400.00, "event,engagement,shoot"),
                    ("Birthday Party", "2-hour party coverage, 75 photos", 350.00, "event,birthday,party"),
                    ("Corporate Event", "4-hour corporate event coverage", 800.00, "event,corporate,business"),
                    ("Concert/Show", "Live performance photography, 50 photos", 500.00, "event,concert,live"),
                ],
                "Commercial": [
                    ("Product Photography (5 items)", "5 product shots on white background", 400.00, "commercial,product,ecommerce"),
                    ("Food Photography", "Styled food photography session", 500.00, "commercial,food,restaurant"),
                    ("Real Estate Photos", "Interior/exterior for property listing", 250.00, "commercial,realestate,property"),
                    ("Brand Content Pack", "20 branded lifestyle images", 1200.00, "commercial,brand,lifestyle"),
                    ("Aerial/Drone Photography", "Drone aerial photography session", 350.00, "commercial,drone,aerial"),
                ],
            }
        },
        "Laundry Services": {
            "slug": "laundry_services", "icon": "shirt", "color": "#14B8A6",
            "description": "Wash and fold, dry cleaning, alterations, and specialty garment care",
            "categories": {
                "Wash & Fold": [
                    ("Regular Wash (per lb)", "Wash, dry, and fold per pound", 2.00, "wash,fold,regular"),
                    ("Bedding Wash (per item)", "Comforter/duvet laundering", 20.00, "wash,bedding,comforter"),
                    ("Towel Service (per lb)", "Towel washing and folding", 1.75, "wash,towel,fold"),
                    ("Express Wash (per lb)", "Same-day wash and fold service", 3.50, "wash,fold,express"),
                    ("Delicates (per lb)", "Hand wash for delicate fabrics", 4.00, "wash,delicates,hand"),
                ],
                "Dry Cleaning": [
                    ("Suit (2-piece)", "Professional dry cleaning for suit", 18.00, "dryclean,suit,professional"),
                    ("Dress", "Dress dry cleaning", 14.00, "dryclean,dress"),
                    ("Shirt/Blouse", "Dress shirt dry cleaning and press", 6.50, "dryclean,shirt,press"),
                    ("Coat/Jacket", "Outerwear dry cleaning", 20.00, "dryclean,coat,jacket"),
                    ("Wedding Dress", "Wedding gown cleaning and preservation", 200.00, "dryclean,wedding,preservation"),
                ],
                "Alterations": [
                    ("Hem Pants", "Pants hemming adjustment", 12.00, "alteration,hem,pants"),
                    ("Take In/Let Out Waist", "Waist adjustment on pants or skirt", 18.00, "alteration,waist,adjust"),
                    ("Zipper Replacement", "Replace broken zipper", 20.00, "alteration,zipper,replace"),
                    ("Button Replacement", "Replace missing or broken buttons", 5.00, "alteration,button,replace"),
                    ("Dress Alteration", "Custom dress fitting and alteration", 45.00, "alteration,dress,fitting"),
                ],
            }
        },
        "Moving Services": {
            "slug": "moving_services", "icon": "box", "color": "#B45309",
            "description": "Local and long-distance moving, packing, storage, and relocation services",
            "categories": {
                "Local Moving": [
                    ("Studio Move", "2 movers, truck, 3 hours for studio/1BR", 350.00, "local,studio,move"),
                    ("1-2 Bedroom Move", "3 movers, truck, 5 hours", 650.00, "local,apartment,move"),
                    ("3+ Bedroom Move", "4 movers, large truck, 8 hours", 1200.00, "local,house,move"),
                    ("Office Move (Small)", "Small office relocation, 3 movers", 800.00, "local,office,move"),
                    ("Furniture Delivery", "Single item or small load delivery", 150.00, "local,furniture,delivery"),
                ],
                "Long Distance": [
                    ("Cross-Town (50+ mi)", "50-100 mile relocation service", 1500.00, "longdistance,crosstown"),
                    ("Interstate Move (Basic)", "Interstate move up to 1-bed apartment", 2500.00, "longdistance,interstate,basic"),
                    ("Interstate Move (Full)", "Full household interstate move", 5000.00, "longdistance,interstate,full"),
                    ("Vehicle Transport", "Car shipping within continental US", 1000.00, "longdistance,vehicle,transport"),
                    ("International Move", "Overseas relocation service", 8000.00, "longdistance,international"),
                ],
                "Packing & Storage": [
                    ("Full Packing Service", "Professional packing of all belongings", 500.00, "packing,full,service"),
                    ("Partial Packing", "Packing for fragile/special items only", 250.00, "packing,partial,fragile"),
                    ("Packing Supplies Kit", "Boxes, tape, bubble wrap kit", 75.00, "packing,supplies,kit"),
                    ("Storage Unit (Monthly)", "5x10 climate-controlled storage", 120.00, "storage,unit,monthly"),
                    ("Large Storage (Monthly)", "10x20 climate-controlled storage", 250.00, "storage,large,monthly"),
                ],
            }
        },
        "Real Estate": {
            "slug": "real_estate", "icon": "building", "color": "#DC2626",
            "description": "Property listings, home buying, selling, rentals, and property management",
            "categories": {
                "Buy/Sell Services": [
                    ("Buyer's Agent Service", "Full buyer representation (commission based)", 0.00, "buysell,buyer,agent"),
                    ("Listing Service", "Full listing with marketing package", 500.00, "buysell,listing,marketing"),
                    ("Home Valuation", "Comparative market analysis report", 150.00, "buysell,valuation,cma"),
                    ("Home Staging", "Professional home staging consultation", 300.00, "buysell,staging,consultation"),
                    ("Open House Hosting", "Professional open house management", 200.00, "buysell,openhouse,hosting"),
                ],
                "Rental Services": [
                    ("Tenant Screening", "Background and credit check for tenants", 50.00, "rental,screening,tenant"),
                    ("Lease Preparation", "Custom residential lease agreement", 150.00, "rental,lease,preparation"),
                    ("Property Management (Monthly)", "Monthly property management fee", 200.00, "rental,management,monthly"),
                    ("Rental Listing", "Professional rental listing with photos", 100.00, "rental,listing,photos"),
                    ("Eviction Processing", "Legal eviction filing and processing", 500.00, "rental,eviction,legal"),
                ],
                "Inspections": [
                    ("Home Inspection", "Full pre-purchase home inspection", 400.00, "inspection,home,prepurchase"),
                    ("Termite Inspection", "Wood-destroying organism inspection", 100.00, "inspection,termite,pest"),
                    ("Radon Testing", "Radon gas testing service", 150.00, "inspection,radon,testing"),
                    ("Roof Inspection", "Professional roof condition assessment", 200.00, "inspection,roof,assessment"),
                    ("Septic Inspection", "Septic system evaluation", 350.00, "inspection,septic,evaluation"),
                ],
            }
        },
    }

    all_sectors = []
    all_items = []

    for sector_name, sdata in sectors_data.items():
        sector = Sector(
            name=sector_name, slug=sdata["slug"],
            description=sdata["description"], icon=sdata["icon"],
            color=sdata["color"], is_active=True, item_count=0
        )
        db.add(sector)
        db.flush()
        all_sectors.append(sector)

        item_count = 0
        for cat_name, items in sdata["categories"].items():
            category = Category(
                sector_id=sector.id, name=cat_name,
                description=f"{cat_name} services for {sector_name}",
                sort_order=list(sdata["categories"].keys()).index(cat_name)
            )
            db.add(category)
            db.flush()

            for item_name, desc, price, tags in items:
                item = Item(
                    sector_id=sector.id, category_id=category.id,
                    name=item_name, description=desc,
                    price=price, is_available=True, tags=tags
                )
                db.add(item)
                all_items.append(item)
                item_count += 1

        sector.item_count = item_count

    db.flush()

    # ===================== ORDERS (15+) =====================
    statuses = ["pending", "confirmed", "processing", "completed", "cancelled"]
    payment_methods = ["credit_card", "debit_card", "paypal", "cash", "apple_pay"]
    addresses = [
        "123 Main St, New York, NY 10001",
        "456 Oak Ave, Los Angeles, CA 90001",
        "789 Elm Blvd, Chicago, IL 60601",
        "321 Pine Dr, Houston, TX 77001",
        "654 Maple Ln, Phoenix, AZ 85001",
        "987 Cedar Ct, Philadelphia, PA 19101",
        "147 Birch Way, San Antonio, TX 78201",
        "258 Walnut Rd, San Diego, CA 92101",
    ]

    regular_users = [u for u in users if u.role == "user"]

    for i in range(20):
        user = random.choice(regular_users)
        sector = random.choice(all_sectors)
        sector_items = [item for item in all_items if item.sector_id == sector.id]
        if not sector_items:
            continue

        order = Order(
            user_id=user.id,
            sector_id=sector.id,
            status=random.choice(statuses),
            notes=random.choice(["", "Please rush", "Call before delivery", "Leave at door", "Handle with care"]),
            shipping_address=random.choice(addresses),
            payment_method=random.choice(payment_methods),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))
        )
        db.add(order)
        db.flush()

        total = 0.0
        num_items = random.randint(1, 4)
        chosen_items = random.sample(sector_items, min(num_items, len(sector_items)))
        for item in chosen_items:
            qty = random.randint(1, 3)
            oi = OrderItem(
                order_id=order.id, item_id=item.id,
                quantity=qty, unit_price=item.price,
                customizations={}
            )
            total += item.price * qty
            db.add(oi)

        order.total = round(total, 2)

    db.commit()
    print(f"Seeded: {len(users_data)} users, {len(all_sectors)} sectors, {len(all_items)} items, 20 orders")
