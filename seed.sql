CREATE TABLE plans (
  id SERIAL PRIMARY KEY,
  plan_name TEXT NOT NULL,
  plan_url TEXT NOT NULL,
  plan_resolution TEXT,
  planning_method TEXT,
  acquisition TEXT,
  easement TEXT,
  stewardship TEXT,
  plan_timeframe TEXT,
  agency_lead TEXT,
  geo_extent TEXT,
  habitat TEXT,
  water_quality TEXT,
  resources_species TEXT,
  community_resilience TEXT,
  ecosystem_resilience TEXT,
  gulf_economy TEXT,
  related_state TEXT
);

COPY plans(plan_name,plan_url,plan_resolution,planning_method,acquisition,easement,stewardship,plan_timeframe,geo_extent,habitat,water_quality,resources_species,community_resilience,ecosystem_resilience,gulf_economy,related_state) 
FROM 'C:\Users\ppatel\Desktop\CIT_Refactored\Refactored_CIT\test.csv' DELIMITER ',' CSV HEADER;

/*FROM 'D:\SCA\app_design_for_tools\inventory_of_plans\flask\test.csv' DELIMITER ',' CSV HEADER;*/


CREATE TABLE newplans (
  id SERIAL PRIMARY KEY,
  plan_name TEXT NOT NULL,
  plan_url TEXT NOT NULL,
  plan_resolution TEXT,
  planning_method TEXT,
  acquisition TEXT,
  easement TEXT,
  stewardship TEXT,
  plan_timeframe TEXT,
  agency_lead TEXT,
  geo_extent TEXT,
  habitat TEXT,
  water_quality TEXT,
  resources_species TEXT,
  community_resilience TEXT,
  ecosystem_resilience TEXT,
  gulf_economy TEXT,
  related_state TEXT,
  status TEXT,
  is_new BOOLEAN,
  existing_planid INTEGER REFERENCES plans(id),
  username TEXT REFERENCES users(username)

);

CREATE TABLE likes (
  id SERIAL PRIMARY KEY,
  user_username TEXT REFERENCES users(username),
  plan_id INTEGER REFERENCES plans(id)
)