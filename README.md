# Flights Test Project

🗎 [Документация API](172.104.135.190:8899/static/docs/index.html) 

В задаче есть расплывчатые формулировки, но поскольку в задании обозначено «умение выполнять задачу имея неполные данные о ней», я не стал подробно уточнять, что такое «оптимальный вариант» и «отличия между результатами двух запросов».

Учитывая это, а так же тот факт, что в одном файле содержатся маршруты в одну сторону, а в другом - в обе, получившиеся методы для сравнения запросов могут иметь сомнительную полезность в реальной жизни. 
Надеюсь, что они хотя бы смогут показать мои способности к написанию кода.

Также надеюсь, что в реальной работе задачи формируются конкретнее, либо есть возможность узнать у потребителя API, что же, всё-таки, тот хочет получить :)   

Оптимальность маршрута я расчитываю по формуле: 
```
((Цена билета) / (Минимальная цена среди результатов)) * ((Длительность полётов) / (Минимальная длительность среди результатов))
``` 

Таким образом, идеальный билет будет иметь оптимальность = 1, а чем она больше, тем хуже.  

## Примеры запросов

### Поиск билета
Самый дешёвый в одну сторону
```
http://172.104.135.190:8899/api/fares/itineraries/?source=dxb&destination=bkk&ordering=price&two_way=false&limit=1
```

Самый быстрый в одну сторону
```
http://172.104.135.190:8899/api/fares/itineraries/?source=dxb&destination=bkk&ordering=duration&two_way=false&limit=1
```

Оптимальный туда-обратно для 2 взрослых и 1 ребёнка
```
http://172.104.135.190:8899/api/fares/itineraries/?source=dxb&destination=bkk&ordering=optimal_score&two_way=true&adult=2&child=1&limit=1
```


### Сравнение

```
http://172.104.135.190:8899/api/fares/diff/?left_request_id=1&right_request_id=2&limit=10
http://172.104.135.190:8899/api/fares/compare/?left_request_id=1&right_request_id=2
```

## Запуск проекта


```
cp ./.env.example ./.env
cp ./.env.db.example ./.env.db
docker-compose up -d --build
docker-compose exec web python3 /app/manage.py migrate
docker-compose exec web python3 /app/manage.py sorcery upgrade
docker-compose exec web python3 /app/manage.py import_reference_data /app-data
docker-compose exec web python3 /app/manage.py import_sample_data /app-data
```
