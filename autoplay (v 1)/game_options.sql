-- Insert SQL Rules Here 
UPDATE GameOptions SET 'Default' = 0 WHERE Type = 'GAMEOPTION_EVENTS';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_QUICK_COMBAT';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_QUICK_MOVEMENT';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_NO_GOODY_HUTS';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_NO_TECH_TRADING';