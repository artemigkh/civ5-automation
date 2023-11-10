-- Insert SQL Rules Here 
UPDATE GameOptions SET 'Default' = 0 WHERE Type = 'GAMEOPTION_EVENTS';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_QUICK_COMBAT';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_QUICK_MOVEMENT';
UPDATE GameOptions SET 'Default' = 1 WHERE Type = 'GAMEOPTION_NO_TECH_TRADING';

UPDATE CustomModOptions SET Value = 1 WHERE Name = 'LOG_MAP_STATE';