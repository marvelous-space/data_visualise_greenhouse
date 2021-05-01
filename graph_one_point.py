import pymysql
import matplotlib.pyplot as plt


def request_one_point(points, t_start, t_stop, _exp_id, sensor_id, cur, default_value):
    value_min_array = []
    value_max_array = []
    value_lost_array = []
    t_real_array = []
    t_lost_array = []

    for (p, t1, t2) in zip(points, t_start, t_stop):
        comm_str = "select time, data from raw_data where exp_id = {} and sensor_id = {} " \
                   "and time > '{}' and time < '{}'".format(
            _exp_id, sensor_id, t1, t2)
        resp = cur.execute(comm_str)
        value_rows = cur.fetchall()
        print(len(value_rows))
        value_array = [x['data'] for x in value_rows]
        if value_array:
            value_min = min(value_array)
            value_max = max(value_array)
            value_min_array.append(value_min)
            value_max_array.append(value_max)
            t_real_array.append(t1)
        else:
            value_lost = default_value
            print('point {} lost, t={}'.format(p, t1))
            value_lost_array.append(value_lost)
            t_lost_array.append(t1)

    return (value_min_array, value_max_array, value_lost_array, t_real_array, t_lost_array)

def one_day_points_graph(_db_params, _exp_id, show=True):
    con = pymysql.connect(host=_db_params["host"],
                          user=_db_params["user"],
                          password=_db_params["password"],
                          # db='experiment',
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor)
    cur = con.cursor()
    cur.execute("use {}".format(_db_params["db"]))

    comm_str = "select distinct(date(end_time)) as day from exp_data where " \
              "is_finished=0 and exp_id={};".format(_exp_id)
    cur.execute(comm_str)
    rows = cur.fetchall()
    # return (_db_params, _search_table, _exp_id)
    days = [x['day'] for x in rows]
    for d in days:
        print(str(d))
  #  t_start = []
   # t_stop = []
    d1 = str(input(("Select day of exp:\n")))

    comm_str = "select point_id, start_time, red, white, end_time from exp_data where date(start_time) = date('{}');".format(d1)
    resp = cur.execute(comm_str)
    rows = cur.fetchall()
    # point_id = rows[0]['point_id']
    points = [x['point_id'] for x in rows]
    reds = [x['red'] for x in rows]
    whites = [x['white'] for x in rows]
    t_start = [x['start_time'] for x in rows]
    t_stop = [x['end_time'] for x in rows]
    # t_start.append(rows[0]['start_time'])
    # t_stop.append(rows[0]['end_time'])

    print(rows)
    # print(point_id)
    print(points)
    print(t_start)
    print(t_stop)

    (co2_min_array, co2_max_array, co2_lost_array, t_real_co2_array, t_lost_co2_array) = \
        request_one_point(points, t_start, t_stop, _exp_id, sensor_id=3, cur=cur, default_value=300)

    (temp_min_array, temp_max_array, temp_lost_array, t_real_temp_array, t_lost_temp_array) = \
        request_one_point(points, t_start, t_stop, _exp_id, sensor_id=5, cur=cur, default_value=30)

    (hum_min_array, hum_max_array, hum_lost_array, t_real_hum_array, t_lost_hum_array) = \
        request_one_point(points, t_start, t_stop, _exp_id, sensor_id=4, cur=cur, default_value=70)

    (press_min_array, press_max_array, press_lost_array, t_real_press_array, t_lost_press_array) = \
        request_one_point(points, t_start, t_stop, _exp_id, sensor_id=2, cur=cur, default_value=100000)

    (mass_min_array, mass_max_array, mass_lost_array, t_real_mass_array, t_lost_mass_array) = \
        request_one_point(points, t_start, t_stop, _exp_id, sensor_id=6, cur=cur, default_value=400)

    con.close()

    # строит графики
    if show:
        # 2D subplots plot
        # fig, axs = plt.subplots(4, 1, sharex=True, figsize=[12, 9])
        #fig, axs = plt.subplots(5, 1, figsize=[12, 9])
        #fig.suptitle("exp={} start_time={}".format(
         #   _exp_id, d))
        fig = plt.figure()
        gs = fig.add_gridspec(6, hspace=0)
        axs = gs.subplots(sharex=True)
        fig.suptitle("exp={}, date={}".format(
             _exp_id, d1))

        axs[0].plot(t_real_co2_array, co2_min_array, "-.og", label='raw co2 data')
        axs[0].grid()
        axs[0].plot(t_real_co2_array, co2_max_array, "-vr", label='raw co2 data')
        axs[0].plot(t_lost_co2_array, co2_lost_array, "Xk", label='raw co2 data')

        axs[1].plot(t_real_temp_array, temp_min_array, "-.og", label='raw temp data')
        axs[1].grid()
        axs[1].plot(t_real_temp_array, temp_max_array, "-vr", label='raw temp data')
        axs[1].plot(t_lost_temp_array, temp_lost_array, "Xk", label='raw temp data')

        axs[2].plot(t_real_hum_array, hum_min_array, "-.og", label='raw hum data')
        axs[2].plot(t_lost_hum_array, hum_lost_array, "Xk", label='raw hum data')
        axs[2].grid()

        axs[3].plot(t_real_press_array, press_min_array, "-.og", label='raw press data')
        axs[3].grid()
        axs[3].plot(t_real_press_array, press_max_array, "-vr", label='raw press data')
        axs[3].plot(t_lost_press_array, press_lost_array, "Xk", label='raw press data')

        axs[4].plot(t_real_mass_array, mass_min_array, "-.og", label='mass raw data')
        axs[4].grid()
        axs[4].plot(t_real_mass_array, mass_max_array, "-vr", label='mass raw data')
        axs[4].plot(t_lost_mass_array, mass_lost_array, "Xk", label='mass raw data')

        axs[5].plot(t_start, reds, "-.og", label='red data')
        axs[5].grid()
        axs[5].plot(t_start, whites, "-vr", label='white data')

        axs[0].set(ylabel='CO2, ppmv')
        axs[1].set(ylabel='temp, °C')
        axs[2].set(ylabel='hum, %')
        axs[3].set(ylabel='Pressure, kPa')
        axs[5].set(ylabel='red, white, mA')
        axs[5].set(xlabel='time')
        axs[4].set(ylabel='mass, g')

        for ax in axs:
            ax.label_outer()
        plt.show()

if __name__ == "__main__":

    db = {
        "host": '10.9.*****',
        "user": '*****',
        "db": 'experiment',
        "password": "********"
    }

    one_day_points_graph(_db_params = db, _exp_id = 9, show=True)