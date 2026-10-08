"""Constants for the ha-tank-os Home Assistant integration."""

DOMAIN = "tank_os"
STORAGE_KEY = "tank_os.data"
STORAGE_VERSION = 1
STORAGE_MINOR_VERSION = 1

SERVICE_CREATE_TANK = "create_tank"
SERVICE_LIST_TANKS = "list_tanks"
SERVICE_UPDATE_TANK = "update_tank"
SERVICE_DELETE_TANK = "delete_tank"
SERVICE_CREATE_LOCATION = "create_location"
SERVICE_LIST_CONTEXT = "list_context"
SERVICE_UPDATE_LOCATION = "update_location"
SERVICE_DELETE_LOCATION = "delete_location"
SERVICE_START_SESSION = "start_measurement_session"
SERVICE_RECORD_OBSERVATION = "record_observation"
SERVICE_LIST_OBSERVATIONS = "list_observations"
SERVICE_UPDATE_OBSERVATION = "update_observation"
SERVICE_DELETE_OBSERVATION = "delete_observation"

SOURCE_MANUAL = "manual"
