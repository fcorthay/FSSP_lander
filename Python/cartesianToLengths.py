import sys
import re
import numpy as np
import time

relative_movement = False
position = [0.0, 0.0, 0.0]
start_position = [0.0, 0.0, 0.0]
displacement = [0.0, 0.0, 0.0]
displacement_speed = 1.0
fixing_points = [
    [0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0]
]
end_of_work = False

verbose = 1
indent = '  '

# ==============================================================================
# functions
#

# ------------------------------------------------------------------------------
# parse displacement values
#
def g_coordinates(parameters, actual_pos):
    """returns 3 coordinates from a g-code"""
                                                                # default values
    x = actual_pos[0]
    y = actual_pos[0]
    z = actual_pos[0]
                                                                    # parse text
    params = parameters.split(' ')
    for param in params:
        coordinate = param[0]
        value = float(param[1:])
        if coordinate == 'x':
            x = value
        elif coordinate == 'y':
            y = value
        elif coordinate == 'z':
            z = value

    return([x, y, z])

# ------------------------------------------------------------------------------
# parse speed value
#
def g_speed(parameters, actual_speed):
    """returns a speed from a g-code"""
                                                                # default values
    speed = actual_speed
                                                                    # parse text
    params = parameters.split(' ')
    for param in params:
        coordinate = param[0]
        value = float(param[1:])
        if coordinate == 'f':
            speed = value

    return(speed)

# ------------------------------------------------------------------------------
# parse time value
#
def g_time(parameters):
    """returns a time from a g-code"""
                                                                 # default value
    time = 0.0
                                                                    # parse text
    params = parameters.split(' ')
    for param in params:
        coordinate = param[0]
        value = float(param[1:])
        if coordinate == 's':
            time = time + value
        elif coordinate == 'p':
            time = time + value * 1.0E-3

    return(time)

# ------------------------------------------------------------------------------
# transform cartesian coordinates to cable lengths
#
def position_to_lengths(position, fixing_points):
    """transform position to lengths"""
    lengths = np.zeros(len(position))
    for coordinate_index in range(len(position)):
        temp = 0
        for fixing_index in range(len(fixing_points)):
            temp = temp + (
                position[coordinate_index] -
                fixing_points[fixing_index][coordinate_index]
            )**2
        lengths[coordinate_index] = np.sqrt(temp)

    return(lengths)

# ------------------------------------------------------------------------------
# send displacement with absolute coordinates
#
def send_absolute(position, fixing_points):
    """returns a time from a g-code"""
                                                             # set absolute mode
    print('g90')
                                                             # send displacement
    lengths = position_to_lengths(position, fixing_points)
    print("g0 x%d y%d z%d" % (lengths[0], lengths[1], lengths[2]))
                                                             # set relative mode
    print('g91')

# ==============================================================================
# main loop
#
while not end_of_work:
    g_code = sys.stdin.readline().lower()
    g_code = re.sub(';.*', '', g_code).rstrip()
    if len(g_code) > 0:
        reply = 'KO'
        if verbose > 0:
            print(g_code)
                                                                  # parse g-code
        parts = g_code.split(' ', 1)
        code = parts[0]

        parameters = ''
        if len(parts) > 1:
            parameters = parts[1]
        code_kind = code[0]
        try:
            code_id = int(code[1:])
        except:
            code_kind = ''
                                                      # G: positioning functions
        if code_kind == 'g':
                                                                        # moving
            if (code_id == 0) or (code_id == 1):
                if relative_movement == False:
                    new_position = g_coordinates(parameters, position)
                    displacement = np.subtract(new_position, position)
                    position = new_position
                else:
                    displacement = g_coordinates(parameters, [0.0, 0.0, 0.0])
                    position = np.add(position, displacement)
                if verbose > 1:
                    print(
                        indent +
                        "moving to position (%d, %d, %d)" % (
                            position[0], position[1], position[2]
                        )
                    )
                    print(
                        indent +
                        "displacement is (%d, %d, %d)" % (
                            displacement[0], displacement[1], displacement[2]
                        )
                    )
                if code_id == 1:
                    displacement_speed = g_speed(parameters, displacement_speed)
                reply = 'OK'
                                                                          # wait
            elif code_id == 4:
                wait_delay = g_time(parameters)
                if verbose > 1:
                    print(indent + "waiting for %.3f sec." % (wait_delay))
                time.sleep(wait_delay)
                reply = 'OK'
                                                             # to start position
            elif code_id == 28:
                displacement = np.subtract(start_position, position)
                position = start_position
                if verbose > 1:
                    print(
                        indent +
                        "moving to start position (%d, %d, %d)" % (
                            position[0], position[1], position[2]
                        )
                    )
                send_absolute(position, fixing_points)
                reply = 'OK'
                                                          # absolute coordinates
            elif code_id == 90:
                relative_movement = False
                if verbose > 1:
                    print(indent + 'entering absolute mode')
                reply = 'OK'
                                                          # relative coordinates
            elif code_id == 91:
                relative_movement = True
                if verbose > 1:
                    print(indent + 'entering relative mode')
                reply = 'OK'
                                                    # M: miscellaneous functions
        if code_kind == 'm':
                                                                  # machine stop
            if code_id == 0:
                end_of_work = True
                if verbose > 1:
                    print(indent + 'stopping the machine')
                reply = 'OK'
                                                                 # fixing points
            elif (code_id == 131) or (code_id == 132) or (code_id == 133):
                index = code_id - 131
                fixing_points[index] = g_coordinates(
                    parameters, fixing_points[index]
                )
                start_position = np.mean(fixing_points, axis=0)
                start_position[2] = start_position[2]/3
                if verbose > 1:
                    print(
                        indent +
                        "new fixing point: (%d, %d, %d)" % (
                            fixing_points[index][0],
                            fixing_points[index][1],
                            fixing_points[index][2]
                        )
                    )
                    print(
                        indent +
                        "new start position: (%d, %d, %d)" % (
                            start_position[0],
                            start_position[1],
                            start_position[2]
                        )
                    )
                reply = 'OK'
    print(reply)

print("\nDone")