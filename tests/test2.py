
import re

llm_response = \
"""
go
### Action Parameters
```
- ?player - human: the player navigating
- ?from - location: the current location
- ?to - location: the adjacent location
```

### Action Preconditions
```
(and
    (at ?player ?from) ; The player is at the current location
    (connected ?from ?to) ; The current location is connected to the adjacent location
)
```

### Action Effects
```
(and
    (not (at ?player ?from)) ; The player is no longer at the current location
    (at ?player ?to) ; The player is now at the adjacent location
)
```

## NEXT ACTION
get
### Action Parameters
```
- ?player - human: the player picking up the item
- ?item - object: the item being picked up
- ?loc - location: the location where the item is present
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at the location
    (at ?item ?loc) ; The item is present at the location
)
```

### Action Effects
```
(and
    (not (at ?item ?loc)) ; The item is no longer at the location
    (inventory ?player ?item) ; The item is now in the player's inventory
)
```

## NEXT ACTION
get_water
### Action Parameters
```
- ?player - human: the player retrieving water
- ?water - water: the water being retrieved
- ?loc - location: the location with a water source
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at the location
    (has_water_source ?loc) ; The location has a water source
)
```

### Action Effects
```
(and
    (inventory ?player ?water) ; The water is now in the player's inventory
)
```

## NEXT ACTION
chop_wood
### Action Parameters
```
- ?player - human: the player chopping wood
- ?wood - wood: the wood being chopped
- ?loc - location: the location with wood
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at the location
    (has_wood ?loc) ; The location has wood
)
```

### Action Effects
```
(and
    (not (has_wood ?loc)) ; The wood is no longer at the location
    (inventory ?player ?wood) ; The wood is now in the player's inventory
)
```

## NEXT ACTION
carve_groove
### Action Parameters
```
- ?player - human: the player carving a groove
- ?wood - wood: the wood being carved
```

### Action Preconditions
```
(and
    (inventory ?player ?wood) ; The player has wood in their inventory
)
```

### Action Effects
```
(and
    (groove ?wood) ; The wood now has a groove carved into it
)
```

## NEXT ACTION
light_fire
### Action Parameters
```
- ?player - human: the player lighting a fire
- ?loc - location: the location where the fire is being lit
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at the location
    (can_light_fire ?loc) ; The location is safe for lighting a fire
)
```

### Action Effects
```
(and
    (has_fire ?loc) ; The location now has a fire going
)
```

## NEXT ACTION
build_shelter
### Action Parameters
```
- ?player - human: the player building a shelter
- ?wood - wood: the wood used for building
- ?loc - location: the location where the shelter is built
```

### Action Preconditions
```
(and
    (inventory ?player ?wood) ; The player has wood in their inventory
    (is_safe ?loc) ; The location is safe to make shelter
)
```

### Action Effects
```
(and
    (has_shelter ?loc) ; The location now has a shelter
)
```

## NEXT ACTION
clean_water
### Action Parameters
```
- ?player - human: the player cleaning water
- ?water - water: the water being cleaned
- ?loc - location: the location with a fire
```

### Action Preconditions
```
(and
    (inventory ?player ?water) ; The player has untreated water in their inventory
    (has_fire ?loc) ; The location has a fire
)
```

### Action Effects
```
(and
    (treated ?water) ; The water is now treated and safe for drinking
)
```

## NEXT ACTION
drink_water
### Action Parameters
```
- ?player - human: the player drinking water
- ?water - water: the water being consumed
```

### Action Preconditions
```
(and
    (inventory ?player ?water) ; The player has water in their inventory
)
```

### Action Effects
```
(and
    (not (inventory ?player ?water)) ; The water is no longer in the player's inventory
    (drank ?player) ; The player has consumed the water
)
```

## NEXT ACTION
find_other_survivors
### Action Parameters
```
- ?player - human: the player searching for survivors
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at a location
)
```

### Action Effects
```
(and
    (has_friend ?player) ; The player may have found a survivor
)
```

## NEXT ACTION
build_raft
### Action Parameters
```
- ?player - human: the player building a raft
- ?raft - raft: the raft being built
```

### Action Preconditions
```
(and
    (inventory ?player ?wood) ; The player has the necessary materials in their inventory
)
```

### Action Effects
```
(and
    (has_escaped ?player) ; The player has built a raft and left with fellow survivors
)
```

## NEXT ACTION
make_weapon
### Action Parameters
```
- ?player - human: the player making a weapon
- ?wood - wood: the wood used for making the weapon
- ?spear - spear: the spear being created
```

### Action Preconditions
```
(and
    (inventory ?player ?wood) ; The player has wood in their inventory
)
```

### Action Effects
```
(and
    (inventory ?player ?spear) ; The player now has a spear
)
```

## NEXT ACTION
hunt_fish
### Action Parameters
```
- ?player - human: the player hunting fish
- ?fish - fish: the fish being caught
- ?loc - location: the location with fish
```

### Action Preconditions
```
(and
    (at ?player ?loc) ; The player is at the location
    (has_fish ?loc) ; The location has fish
)
```

### Action Effects
```
(and
    (inventory ?player ?fish) ; The fish is now in the player's inventory
)
```

## NEXT ACTION
cook_fish
### Action Parameters
```
- ?player - human: the player cooking fish
- ?fish - fish: the fish being cooked
- ?loc - location: the location with a fire
```

### Action Preconditions
```
(and
    (inventory ?player ?fish) ; The player has fish in their inventory
    (has_fire ?loc) ; The location has a fire
)
```

### Action Effects
```
(and
    (cooked ?fish) ; The fish is now cooked
)
```
"""

raw_actions = llm_response.split('## NEXT ACTION')

print(raw_actions)
        
actions = []
for i in raw_actions:
    # define the regex patterns
    action_pattern = re.compile(r'\[([^\]]+)\]')
    rest_of_string_pattern = re.compile(r'\[([^\]]+)\](.*)', re.DOTALL)
    
    # search for the action name
    action_match = action_pattern.search(i)
    action_name = action_match.group(1) if action_match else None
    
    # extract the rest of the string
    rest_match = rest_of_string_pattern.search(i)
    rest_of_string = rest_match.group(2).strip() if rest_match else None
    
    # actions.append(parse_action(llm_response=rest_of_string, action_name=action_name))
    
    actions.append(rest_of_string)
    
print(actions)
