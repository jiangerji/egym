#encoding=utf-8

import random

import geohash

def randomLongitude():
    return random.randint(-160, 160) + random.randint(0, 100000) * 0.000001

def randomLatitude():
    return random.randint(-88, 88) + random.randint(0, 100000) * 0.000001

def randomPosition():
    return (randomLatitude(), randomLongitude())

# 测试打印几个经纬度附近点的geohash
def a():
    latitude = randomLatitude()
    longitude = randomLongitude()

    print geohash.encode(latitude, longitude)

    print geohash.encode(latitude + 0.001, longitude)    
    print geohash.encode(latitude + 0.1, longitude)    
    print geohash.encode(latitude - 0.001, longitude + 0.001)

# 检查geohash编码和解码是否正确
def checkEncodeAndDecode():
    count = 0
    for i in range(100):
        latitude, longitude = randomPosition()
        try:
            hashcode = geohash.encode(latitude, longitude)
            # print "encode", hashcode, latitude, longitude

            decodeLatitude, decodeLongitude = geohash.decode(hashcode)
            # print "decode", "%.6f %.6f"%(decodeLatitude, decodeLongitude)


            latitudeIsOK = decodeLatitude < latitude + 0.000001 and decodeLatitude > latitude - 0.000001
            longitudeIsOK = decodeLongitude < longitude + 0.000001 and decodeLongitude > longitude - 0.000001

            if not (latitudeIsOK and longitudeIsOK):
                print latitude, longitude, decodeLatitude, decodeLongitude
                count += 1

        except Exception, e:
            print "error:", latitude, longitude
            # break
    if count > 0:
        print "error"

import math
# 获取起点和终点的公里数
def getDistance(start, end):
    startLat, startLon = start
    endLat, endLon = end

    lat1 = startLat * math.pi / 180
    lat2 = endLat * math.pi / 180

    lon1 = startLon * math.pi / 180
    lon2 = endLon * math.pi / 180

    a = lat1 - lat2
    b = lon1 - lon2

    r = 6378.137

    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2),2) +
    math.cos(lat1)*math.cos(lat2)*math.pow(math.sin(b/2),2)))

    s *= r
    return s

# 测试获取公里数
def b():
    latitude = float("%.4f"%randomLatitude())
    longitude = float("%.4f"%randomLongitude())

    print latitude, longitude

    start = (latitude, longitude)

    for i in range(100):
        # print geohash.encode(float(latitude), float(longitude))
        end = (latitude + random.randint(0, 499) * 0.000001, longitude + random.randint(0, 499) * 0.000001)
        # print geohash.encode(end[0], end[1])
        
        print end
        print "distance", getDistance(start, end)

    print 
    end = (latitude + 0.0005, longitude + 0.0005)
    print "distance", getDistance(start, end)


import sqlite3

latitude = 30.178903
longitude = 45.698545

def testLBS():
    cx = sqlite3.connect("lbs.db")
    cx.execute('CREATE  TABLE  IF NOT EXISTS "lbs" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "latitude" FLOAT NOT NULL , "longitude" FLOAT NOT NULL , "geohash" VARCHAR(12) NOT NULL )')

    insertCmd = 'INSERT INTO "lbs" ("latitude","longitude","geohash") VALUES (?,?,?)'

    # 生成100000个半径100多公里范围位置信息
    if False:
        for i in xrange(10**5):
            deltaLat = random.randint(-1, 1) + random.randint(0, 350000) * 0.000001
            deltaLon = random.randint(-1, 1) + random.randint(0, 350000) * 0.000001

            realLat = latitude + deltaLat
            realLon = longitude + deltaLon
            posGeoHash = geohash.encode(float("%.2f"%realLat), float("%.2f"%realLon))
            cx.execute(insertCmd, ("%.6f"%realLat, "%.6f"%realLon, posGeoHash))
    cx.commit()

    cu.close()
    cx.close()

# 获取距离内的位置
def getNeighbours(levelQuota=1):
    cx = sqlite3.connect("lbs.db")

    selectCmd = "select * from lbs where geohash='%s'"

    # 找出最近的item
    cu=cx.cursor()
    orthLatitude = float("%.2f"%(math.floor(latitude*100)/100))
    orthLongitude = float("%.2f"%(math.floor(longitude*100)/100))

    latlon = (orthLatitude, orthLongitude)
    print latlon, geohash.encode(orthLatitude, orthLongitude)

    # levelQuota = level
    for level in range(1, levelQuota):
        neighbours = getNeighbourArea(latlon, level)
        print "Level", level
        for i in neighbours:
            lat, lon = geohash.decode(i)
            cmd = selectCmd%i
            cu.execute(cmd)
            datas = cu.fetchall()
            if len(datas) > 0:
                for data in datas:
                    nLat = data[1]
                    nLon = data[2]
                    # print i
                    distance = getDistance((latitude, longitude), (nLat, nLon))
                    print "  %10d %f %f %6d"%(data[0], nLat, nLon, distance*1000), i


def getNeighbourArea(latlon, level=1):
    latitude = latlon[0]
    longitude = latlon[1]

    neighbours = set()

    lat = latitude - level * 0.01
    lon = longitude - level * 0.01

    for i in range(2*level + 1):
        neighbours.add(geohash.encode(lat, lon + i * 0.01))

    for i in range(2*level + 1):
        neighbours.add(geohash.encode(lat + i * 0.01, lon))

    lat = latitude - level * 0.01
    lon = longitude + level * 0.01

    for i in range(2*level + 1):
        neighbours.add(geohash.encode(lat + i * 0.01, lon))

    lat = latitude + level * 0.01
    lon = longitude - level * 0.01

    for i in range(2*level + 1):
        neighbours.add(geohash.encode(lat, lon + i * 0.01))

    return neighbours

# testLBS()
getNeighbours(levelQuota=5)

# python -m profile -s time test_genhash.py
         