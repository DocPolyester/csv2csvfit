#!/usr/bin/python3.9


import csv,argparse,sys
from os.path import exists

from datetime import datetime, timezone





argParser = argparse.ArgumentParser()
argParser.add_argument("-i","-input",type=str, help="CSV input file", required=True)
argParser.add_argument("-o","-output",type=str, help="FIT compliant CSV output file", required=True)
argParser.add_argument("-f", help="Overwrite output file", action="store_true")
args = argParser.parse_args()


if not exists(args.i):
    print('input file doesnt exist')
    sys.exit()

csv_filename = args.i

if exists(args.o) and not args.f:
    print('output file already exist')
    sys.exit()

output_filename = args.o

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def convert_decimal(row):
    for key,value in row.items():
         value = str(value).replace(',', '.')
         row[key] = value
    return row

def joule_to_cal(work):
    return work/4184

stroke_index = 0
timestamp_index = 1
distance_index = 2
work_index = 3
act_pow_index = 4
avg_pow_index = 5
act_split_index = 6
avg_split_index = 7
stroke_rate_index = 8
heart_rate_index = 9


try:
    time_file_string = csv_filename.rsplit('_')[0]

    fmt = '%Y-%m-%dT%H%M%S'
    tstamp1 = datetime.strptime(time_file_string, fmt)
    FIT_epoch = datetime.strptime('1989-12-31 000000', '%Y-%m-%d %H%M%S')
    start_time = int((tstamp1 - FIT_epoch).total_seconds())
except:
    print('Please use SMARTROW name format for input file. For example: \"2023-12-13T180555_10000m.csv\"')
    sys.exit()

with open(csv_filename) as csvfile:

    reader = csv.DictReader(csvfile, delimiter=';')

    print_string = ['Type,Local Number,Message,Field 1,Value 1,Units 1,Field 2,Value 2,Units 2,Field 3,Value 3,Units 3,Field 4,Value 4,Units 4,Field 5,Value 5,Units 5,Field 6,Value 6,Units 6']

    print_string = print_string + [str('Definition,0,file_id,serial_number,1,,time_created,1,,manufacturer,1,,product,1,,number,1,,type,1,')]#pace,1,')]
    print_string = print_string + [str('Data,0,file_id,serial_number,\"3453777148\",,time_created,\"'+str(start_time)+'\",,manufacturer,1,,garmin_product,3907,,type,4,')]

    print_string = print_string + [str('Definition,1,record,timestamp,1,,distance,1,,heart_rate,1,,cadence,1,,power,1,calories,1,')]


    total_strokes =0
    total_work=0.0
    max_heart_rate =0
    avg_heart_rate =0
    max_cadence =0
    avg_cadence =0

    previous_distance=0.0
    previous_timestamp=0

    for row in reader:
        keys = list(row)

        #fill empty data with zeros

        row = {k: "0" if v==" " else v for k, v in row.items() }

        #check for buggy smartrow data and skip if stroke rate is >=60 (if speed > 6,5m/s = 23,4km/h)
        try:
#            current_speed = (float(row[keys[distance_index]]) - previous_distance)/(int(row[keys[timestamp_index]])-previous_timestamp)
#            if current_speed>=5.5:
            timespan_difference = int(row[keys[timestamp_index]])-previous_timestamp
            if timespan_difference <= 1:
                row[keys[timestamp_index]] = str(int(row[keys[timestamp_index]])+2-timespan_difference)
        except:
            continue

        total_strokes = total_strokes + 1
        row = convert_decimal(row)
        print_string = print_string + [str('Data,1,record,timestamp,\"'+str(int(row[keys[timestamp_index]])+start_time)+'\",s,distance,\"'+str(float(row[keys[distance_index]]))+'\",m,heart_rate,\"'+str(row[keys[heart_rate_index]])+'\",bpm,cadence,\"'+str(float(row[keys[stroke_rate_index]]))+'\",rpm,power,\"'+str(row[keys[act_pow_index]])+'\",watts,calories,\"'+str(round(float(row[keys[work_index]])/1000,1))+'\",calories')]
        previous_distance =float(row[keys[distance_index]])
        previous_timestamp = int(row[keys[timestamp_index]])
        total_elapsed_time = str(row[keys[timestamp_index]])
        total_work = total_work + float(row[keys[work_index]])

        if int(row[keys[heart_rate_index]]) > max_heart_rate:
            max_heart_rate = int(row[keys[heart_rate_index]])

        if float(row[keys[stroke_rate_index]]) > max_cadence:
            max_cadence = float(row[keys[stroke_rate_index]])

        avg_cadence = avg_cadence + float(row[keys[stroke_rate_index]])
        avg_heart_rate = avg_heart_rate + int(row[keys[heart_rate_index]])


    avg_cadence = round(avg_cadence / total_strokes,1)
    avg_heart_rate = int(avg_heart_rate / total_strokes)
    total_distance = str(round(float(row[keys[distance_index]]),-2))
    total_strokes = str(total_strokes)

    # I use the concept2 calories model,
    total_calories = round((float(total_work)/float(total_elapsed_time)*4*0.8604+300)*float(total_elapsed_time)/3600,2)


    print_string = print_string +['Definition,11,session,start_time,1,,total_elapsed_time,1,,total_distance,1,,total_strokes,1,,sport_profile_name,128,,sport,1,,sub_sport,1,']
    print_string = print_string +['Data,11,session,start_time,\"'+str(start_time)+'\",s,total_elapsed_time,\"'+total_elapsed_time+'\",s,total_distance,\"'+total_distance+'\",m,total_strokes,\"'+total_strokes+'\",cycles,sport_profile_name,Waterrower,,sport,15,,sub_sport,14,']

    print_string = print_string+[str('Definition,12,activity,timestamp,1,,total_timer_time,1,,local_timestamp,1,,num_sessions,1,,type,1,,event,1,,event_type,1,,event_group,1,,')]
    print_string = print_string+[str('Data,12,activity,timestamp,\"'+str(start_time)+'\",,total_timer_time,\"'+total_elapsed_time+'\",s,local_timestamp,\"'+str(start_time)+'\",,num_sessions,1,,type,0,,event,26,,event_type,1,')]


    print_string = print_string +[str('Definition,5,lap,timestamp,1,,start_time,1,,start_position_lat,1,,start_position_long,1,,end_position_lat,1,,end_position_long,1,,total_elapsed_time,1,,total_timer_time,1,,total_distance,1,,total_cycles,1,,total_work,1,,total_moving_time,1,,time_standing,1,,avg_left_power_phase,4,,avg_left_power_phase_peak,4,,avg_right_power_phase,4,,avg_right_power_phase_peak,4,,avg_power_position,2,,max_power_position,2,,enhanced_avg_speed,1,,enhanced_max_speed,1,,enhanced_avg_altitude,1,,enhanced_min_altitude,1,,enhanced_max_altitude,1,,total_grit,1,,avg_flow,1,,message_index,1,,total_calories,1,,total_fat_calories,1,,avg_power,1,max_power,1,,total_ascent,1,,total_descent,1,,num_lengths,1,,normalized_power,1,,left_right_balance,1,,first_length_index,1,,avg_stroke_distance,1,,num_active_lengths,1,,wkt_step_index,1,,avg_vertical_oscillation,1,,avg_stance_time_percent,1,,avg_stance_time,1,,stand_count,1,,avg_vertical_ratio,1,,avg_stance_time_balance,1,,avg_step_length,1,,enhanced_avg_respiration_rate,1,,enhanced_max_respiration_rate,1,,event,1,,event_type,1,,avg_heart_rate,1,,max_heart_rate,1,,avg_cadence,1,,max_cadence,1,,intensity,1,,lap_trigger,1,,sport,1,,event_group,1,,swim_stroke,1,,sub_sport,1,,avg_temperature,1,,max_temperature,1,,avg_fractional_cadence,1,,max_fractional_cadence,1,,total_fractional_cycles,1,,avg_left_torque_effectiveness,1,,avg_right_torque_effectiveness,1,,avg_left_pedal_smoothness,1,,avg_right_pedal_smoothness,1,,avg_combined_pedal_smoothness,1,,avg_left_pco,1,,avg_right_pco,1,,avg_cadence_position,2,,max_cadence_position,2,,min_temperature,1,,total_fractional_ascent,1,,total_fractional_descent,1,')]

    print_string = print_string +[str('Data,5,lap,timestamp,\"'+str(int(row[keys[timestamp_index]])+start_time)+'\",s,start_time,\"'+str(start_time)+'\",,total_elapsed_time,\"'+total_elapsed_time+'\",s,total_timer_time,\"'+total_elapsed_time+'\",s,total_distance,\"'+total_distance+'\",m,total_strokes,\"'+total_strokes+'\",cycles,enhanced_avg_speed,\"0.0\",m/s,message_index,0,,total_calories,\"'+str(total_calories)+'\",kcal,total_work,\"'+str(round(total_work,2))+'\",kilojoule,event,9,,event_type,1,,avg_heart_rate,\"'+str(avg_heart_rate)+'\",bpm,max_heart_rate,\"'+str(max_heart_rate)+'\",bpm,avg_cadence,\"'+str(avg_cadence)+'\",rpm,max_cadence,\"'+str(max_cadence)+'\",rpm,intensity,0,,lap_trigger,0,,sport,15,,sub_sport,14,,avg_fractional_cadence,0.0,rpm,max_fractional_cadence,0.0,rpm')]




with open(output_filename, 'w', encoding='utf-8') as csv_file:
    #writer = csv.writer(csv_file, delimiter=',')#,quoting=csv.QUOTE_MINIMAL)# quoting=csv.QUOTE_NONE, escapechar='.')

    for row in print_string:
        #print(row)
        csv_file.write(row+'\n')
