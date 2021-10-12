


#def problems(flag):
#    db_sess = db_session.create_session()
#    flag_date = 0
#    lst_backlight = ['-outline', '-outline']
#    region = 'все'
#    lst_backlight[flag_date] = ''
#    list_problems = []
#    if not flag:
#        if current_user.is_authenticated:
#            user = db_sess.query(User).filter(User.email == current_user.email).first()
#    for i in db_sess.query(Complaint).all():
#        if i.n_confirmation >= QUANTITY_CONFIRMATION:
#            flag = True
#        else:
#            flag = False
#        if f'{i.id}.jpg' not in os.listdir('static/img/img_problems'):
#            write_to_file(i.photo, f'static/img/img_problems/{i.id}.jpg')
#        diction = {}
#        diction['id'] = i.id
#        diction['name'] = i.name
#        diction['text'] = i.description
#        diction['lat'] = i.coordinates.split(',')[0]
#        diction['lon'] = i.coordinates.split(',')[1]
#        diction['datetime'] = i.modifed_date
#        diction['date'] = transformation_date(str(i.modifed_date))
#        diction['category'] = i.category
#        diction['n_ver'] = i.n_confirmation
#        diction['ver'] = flag
#        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
#        diction['label'] = DICT_COLORS_LABELS[i.category]
#        if current_user.is_authenticated:
#            diction['pub'] = 0
#            if user.ver_problems:
#                if str(i.id) in user.ver_problems.split(','):
#                    diction['pub'] = -1
#            if user.my_problems:
#                if str(i.id) in user.my_problems.split(','):
#                    diction['pub'] = 1
#        # print(geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text'])
#        if not flag:
#            if region != 'все' and region in \
#                    geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text']:
#                list_problems.append(diction)
#            elif region == 'все':
#                list_problems.append(diction)
#        else:
#            if str(i.id) in user.my_problems.split(','):
#                if region != 'все' and region in \
#                        geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text']:
#                    list_problems.append(diction)
#                elif region == 'все':
#                    list_problems.append(diction)
#    if flag_date == 0:
#        list_problems.sort(key=operator.itemgetter('datetime'), reverse=True)
#    else:
#        list_problems.sort(key=operator.itemgetter('n_ver'), reverse=True)
#    with open('static/txt/regions.txt', 'r', encoding='utf-8') as file:
#        lst = file.readlines()
#    return [list_problems, lst, lst_backlight]
