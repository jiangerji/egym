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

print latitude, longitude

# tttLa, tttLo = (30.189125, 45.699383)
# print getDistance((latitude, longitude), (tttLa, tttLo))
# exit()

def testLBS():
    cx = sqlite3.connect("lbs.db")
    cx.execute('CREATE  TABLE  IF NOT EXISTS "lbs" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "latitude" FLOAT NOT NULL , "longitude" FLOAT NOT NULL , "geohash" VARCHAR(12) NOT NULL , "geohash2" VARCHAR(12) NOT NULL , "geohash5" VARCHAR(12) NOT NULL , "geohash10" VARCHAR(12) NOT NULL , "distance" INTEGER NOT NULL )')

    insertCmd = 'INSERT INTO "lbs" ("latitude","longitude","geohash","geohash2","geohash5","geohash10", "distance") VALUES (?,?,?,?,?,?,?)'

    # 生成100000个半径100多公里范围位置信息
    if True:
        for i in xrange(10**5):
            deltaLat = random.randint(-1, 1) + random.randint(0, 350000) * 0.000001
            deltaLon = random.randint(-1, 1) + random.randint(0, 350000) * 0.000001

            tLat = float("%.6f"%(latitude + deltaLat))
            tLon = float("%.6f"%(longitude + deltaLon))

            # realLat = float("%.2f"%(latitude + deltaLat))
            # realLon = float("%.2f"%(longitude + deltaLon))
            realLat = (int(tLat*100)) / 100.0
            realLon = (int(tLon*100)) / 100.0

            # 0.01表示1公里左右的区域
            posGeoHash = geohash.encode(realLat, realLon)

            # 0.02表示2公里
            realLat_2 = (int(realLat*100) / 2 * 2) / 100.0
            realLon_2 = (int(realLon*100) / 2 * 2) / 100.0
            posGeoHash_2 = geohash.encode(realLat_2, realLon_2)

            # 0.05表示5公里直径的区域
            realLat_5 = (int(realLat*100) / 5 * 5) / 100.0
            realLon_5 = (int(realLon*100) / 5 * 5) / 100.0
            posGeoHash_5 = geohash.encode(realLat_5, realLon_5)

            # 0.1 表示10公里左右
            realLat_10 = (int(tLat*10)) / 10.0
            realLon_10 = (int(tLon*10)) / 10.0
            posGeoHash_10 = geohash.encode(realLat_10, realLon_10)

            distance = int(1000*getDistance((latitude, longitude), (tLat, tLon)))

            cx.execute(insertCmd, (tLat, tLon, posGeoHash, posGeoHash_2, posGeoHash_5, posGeoHash_10, distance))
    cx.commit()
    cx.close()

# 获取距离内的位置
def getNeighbours(levelQuota=1):
    if levelQuota > 4:
        levelQuota = 4
    elif levelQuota < 1:
        levelQuota = 1

    cx = sqlite3.connect("lbs.db")

    selectCmd = "select * from lbs where geohash='%s'"

    latlons = []

    # 找出最近的item
    cu=cx.cursor()
    orthLatitude = float("%.2f"%(math.floor(latitude*100)/100))
    orthLongitude = float("%.2f"%(math.floor(longitude*100)/100))
    latlon = (orthLatitude, orthLongitude)
    latlons.append(latlon)

    orthLatitude_2 = (int(latitude*100) / 2 * 2) / 100.0
    orthLongitude_2 = (int(longitude*100) / 2 * 2) / 100.0
    latlon = (orthLatitude_2, orthLongitude_2)
    latlons.append(latlon)

    orthLatitude_5 = (int(latitude*100) / 5 * 5) / 100.0
    orthLongitude_5 = (int(longitude*100) / 5 * 5) / 100.0
    latlon = (orthLatitude_5, orthLongitude_5)
    latlons.append(latlon)
    
    orthLatitude_10 = float("%.1f"%(math.floor(latitude*10)/10))
    orthLongitude_10 = float("%.1f"%(math.floor(longitude*10)/10))
    latlon = (orthLatitude_10, orthLongitude_10)
    latlons.append(latlon)

    print latlons

    # levelQuota = level
    for level in range(1, levelQuota+1):
        latlon = latlons[level-1]
        print "Level", level, latlon
        getNeighbourArea_1(cu, latlon, level)
        break

def getNeighbourArea_1(cursor, latlon, level=1):
    level = 1

    sLatitude = latlon[0]
    sLongitude = latlon[1]

    geohashCode = geohash.encode(sLatitude, sLongitude)
    selectCmdFormat = "select * from lbs where geohash='%s';"

    # 获取加上相邻的25个象限
    orthLatitude = float("%.2f"%(math.floor(latitude*100)/100))
    orthLongitude = float("%.2f"%(math.floor(longitude*100)/100))
    # print orthLatitude, orthLongitude

    latlons = []
    for i in range(5):
        tLat = float("%.2f"%((int(orthLatitude*100) + (i-2)) / 100.0))
        for j in range(5):
            tLon = float("%.2f"%((int(orthLongitude*100) + (j-2)) / 100.0))
            latlons.append((tLat, tLon))

    print latlons

    # 查询象限区域内的点
    selectParams = ["geohash", "geohash2", "geohash5", "geohash10"]
    selectCmdFormat = "select * from lbs where %s='%s' order by id;"

    for latlon in latlons:
        geohashCode = geohash.encode(latlon[0], latlon[1])
        selectCmd = selectCmdFormat%(selectParams[level-1], geohashCode)

        cursor.execute(selectCmd)
        datas = cursor.fetchall()
        if len(datas) > 0:
            for data in datas:
                nLat = data[1]
                nLon = data[2]
                distance = getDistance((latitude, longitude), (nLat, nLon))
                print "  %10d %f %f %6d"%(data[0], nLat, nLon, distance*1000)


def getNeighbourArea(cursor, latlon, level=1):
    if level < 1:
        level = 1
    elif level > 4:
        level = 4

    sLatitude = latlon[0]
    sLongitude = latlon[1]

    geohashCode = geohash.encode(sLatitude, sLongitude)

    selectParams = ["geohash", "geohash2", "geohash5", "geohash10"]
    selectCmdFormat = "select * from lbs where %s='%s';"

    selectCmd = selectCmdFormat%(selectParams[level-1], geohashCode)
    print selectCmd

    cursor.execute(selectCmd)
    datas = cursor.fetchall()
    if len(datas) > 0:
        for data in datas:
            nLat = data[1]
            nLon = data[2]
            # print i
            distance = getDistance((latitude, longitude), (nLat, nLon))
            print "  %10d %f %f %6d"%(data[0], nLat, nLon, distance*1000)

def getNeighbourArea1(latlon, level=1):
    if level < 1:
        level = 1
    elif level > 4:
        level = 4

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
         