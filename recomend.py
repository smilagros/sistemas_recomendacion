# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 22:09:56 2020

@author: USUARIO
"""
import codecs
import math
from math import sqrt

users = {"Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0,
                      "Norah Jones": 4.5, "Phoenix": 5.0,
                      "Slightly Stoopid": 1.5,
                      "The Strokes": 2.5, "Vampire Weekend": 2.0},

         "Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5,
                  "Deadmau5": 4.0, "Phoenix": 2.0,
                  "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0},

         "Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0,
                  "Deadmau5": 1.0, "Norah Jones": 3.0, "Phoenix": 5,
                  "Slightly Stoopid": 1.0},

         "Dan": {"Blues Traveler": 3.0, "Broken Bells": 4.0,
                 "Deadmau5": 4.5, "Phoenix": 3.0,
                 "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                 "Vampire Weekend": 2.0},

         "Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0,
                    "Norah Jones": 4.0, "The Strokes": 4.0,
                    "Vampire Weekend": 1.0},

         "Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0,
                    "Norah Jones": 5.0, "Phoenix": 5.0,
                    "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                    "Vampire Weekend": 4.0},

         "Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0,
                 "Norah Jones": 3.0, "Phoenix": 5.0,
                 "Slightly Stoopid": 4.0, "The Strokes": 5.0},

         "Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0,
                      "Phoenix": 4.0, "Slightly Stoopid": 2.5,
                      "The Strokes": 3.0}
         }


class recommender:

    def __init__(self, data, k=1, metric='pearson', n=5):
        """ initialize recommender
        currently, if data is dictionary the recommender is initialized
        to it.
        For all other data types of data, no initialization occurs
        k is the k value for k nearest neighbor
        metric is which distance formula to use
        n is the maximum number of recommendations to make"""
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        # Name of the metric
        self.metric = metric
        if self.metric == 'pearson':
            self.fn = self.pearson
        elif self.metric == 'manhattan':
            self.fn = self.manhattan
        elif self.metric == 'euclidiana':
            self.fn = self.euclidiana
        elif self.metric == 'coseno':
            self.fn = self.coseno
        else:
            self.fn = self.pearson

        #
        # if data is dictionary set recommender data to it
        #
        if type(data).__name__ == 'dict':
            self.data = data

    def convertProductID2name(self, id):
        """Given product id number return product name"""
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id

    def userRatings(self, id, n):
        """Return n top ratings for user with id"""
        print("Ratings for " + self.userid2name[id])
        ratings = self.data[id]
        print(len(ratings))
        ratings = list(ratings.items())
        ratings = [(self.convertProductID2name(k), v)
                   for (k, v) in ratings]
        # finally sort and return
        ratings.sort(key=lambda artistTuple: artistTuple[1],
                     reverse=True)
        ratings = ratings[:n]
        for rating in ratings:
            print("%s\t%i" % (rating[0], rating[1]))

    def loadBookDB(self, path=''):
        """loads the BX book dataset. Path is where the BX files are
        located"""
        self.data = {}
        i = 0
        #
        # First load book ratings into self.data
        #
        f = codecs.open(path + "BX-Book-Ratings.csv", 'r', 'utf8')
        for line in f:
            i += 1
            # separate line into fields
            fields = line.split(';')
            user = fields[0].strip('"')
            book = fields[1].strip('"')
            rating = int(fields[2].strip().strip('"'))
            if user in self.data:
                currentRatings = self.data[user]
            else:
                currentRatings = {}
            currentRatings[book] = rating
            self.data[user] = currentRatings
        f.close()
        #
        # Now load books into self.productid2name
        # Books contains isbn, title, and author among other fields
        #
        f = codecs.open(path + "BX-Books.csv", 'r', 'utf8')
        for line in f:
            i += 1
            # separate line into fields
            fields = line.split(';')
            isbn = fields[0].strip('"')
            title = fields[1].strip('"')
            author = fields[2].strip().strip('"')
            title = title + ' by ' + author
            self.productid2name[isbn] = title
        f.close()
        #
        #  Now load user info into both self.userid2name and
        #  self.username2id
        #
        f = codecs.open(path + "BX-Users.csv", 'r', 'utf8')
        for line in f:
            i += 1
            print(line)
            # separate line into fields
            fields = line.split(';')
            userid = fields[0].strip('"')
            location = fields[1].strip('"')
            if len(fields) > 3:
                age = fields[2].strip().strip('"')
            else:
                age = 'NULL'
            if age != 'NULL':
                value = location + '  (age: ' + age + ')'
            else:
                value = location
            self.userid2name[userid] = value
            self.username2id[location] = userid
        f.close()
        print(i)

    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # now compute denominator
        denominator = (sqrt(sum_x2 - pow(sum_x, 2) / n)
                       * sqrt(sum_y2 - pow(sum_y, 2) / n))
        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator

    def manhattan(self, rating1, rating2):
        """Computes the Manhattan distance. Both rating1 and rating2 are dictionaries
           of the form {'The Strokes': 3.0, 'Slightly Stoopid': 2.5}"""
        distance = 0
        commonRatings = False
        for key in rating1:
            if key in rating2:
                distance += abs(rating1[key] - rating2[key])
                commonRatings = True
        if commonRatings:
            return distance
        else:
            return -1  # Indicates no ratings in common

    def euclidiana(self, rating1, rating2):
        """Computes the Euclidean distance. Both rating1 and rating2 are dictionaries
           of the form {'The Strokes': 3.0, 'Slightly Stoopid': 2.5}"""
        distance = 0
        commonRatings = False
        for key in rating1:
            if key in rating2:
                distance += math.pow(rating1[key] - rating2[key], 2)
                commonRatings = True
        if commonRatings:
            return math.sqrt(distance)
        else:
            return -1  # Indicates no ratings in common

    def coseno(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        sqr_sum_x2 = math.sqrt(sum_x2)
        sqr_sum_y2 = math.sqrt(sum_y2)
        # now compute denominator
        denominator = (sqr_sum_x2 * sqr_sum_y2)
        if denominator == 0:
            return 0
        else:
            return sum_xy / denominator

    def computeNearestNeighbor(self, username):
        """creates a sorted list of users based on their distance to
        username"""
        distances = []
        print("\n----------Distance type", self.metric, '----------------------------------------')
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username],
                                   self.data[instance])
                distances.append((instance, distance))
                print(username, "-", instance, ":", distance)
        # sort based on distance -- closest first
        distances.sort(key=lambda artistTuple: artistTuple[1],
                       reverse=True)

        return distances

    def recommend(self, user):
        """Give list of recommendations"""
        recommendations = {}
        # first get list of users  ordered by nearness
        nearest = self.computeNearestNeighbor(user)
        #print("Vecinos cercanos:", nearest)
        #
        # now get the ratings for the user
        #
        userRatings = self.data[user]
        #print("User Ratings:", userRatings)
        #
        # determine the total distance
        totalDistance = 0.0
        for i in range(self.k):
            totalDistance += nearest[i][1]
        #print("Distance:", totalDistance)
        # now iterate through the k nearest neighbors
        # accumulating their ratings
        #print("\n++++++++++++++Starting Recomendations++++++++++++++++")
        for i in range(self.k):
            # compute slice of pie
            weight = nearest[i][1] / totalDistance
            #print("Weight:", weight)
            # get the name of the person
            name = nearest[i][0]
            #print("\nNeighbor:", name)
            # get the ratings for this person
            neighborRatings = self.data[name]
            #print("User ratings:", userRatings)
            #print("Neighbor ratings:", neighborRatings)
            # get the name of the person
            # now find bands neighbor rated that user didn't
            for artist in neighborRatings:
                #print("artist:", artist)
                if not artist in userRatings:
                    if artist not in recommendations:
                        recommendations[artist] = (neighborRatings[artist]
                                                   * weight)
                        #print("Recomendacion", artist, "-", recommendations[artist])
                    else:
                        recommendations[artist] = (recommendations[artist]
                                                   + neighborRatings[artist]
                                                   * weight)
                        #print("Recomendacion", artist, "-", recommendations[artist])
                else:
                    pass#print(" No Recomendacion")

        # now make list from dictionary
        recommendations = list(recommendations.items())
        recommendations = [(self.convertProductID2name(k), v)
                           for (k, v) in recommendations]
        # finally sort and return
        recommendations.sort(key=lambda artistTuple: artistTuple[1],
                             reverse=True)
        # Return the first n items
        print("\n-> Recomendaciones Finales 2=", recommendations[:self.n], "para:", user)

        return recommendations[:self.n]


recomendacion1 = recommender(users, 5, 'pearson', 5)
recomendacion2 = recommender(users, 5, 'manhattan', 5)
recomendacion3 = recommender(users, 5, 'euclidiana', 5)
recomendacion4 = recommender(users, 5, 'coseno', 5)
recomendacion1.recommend('Angelica')
recomendacion2.recommend('Angelica')
recomendacion3.recommend('Angelica')
recomendacion4.recommend('Angelica')

recomendacion1.recommend('Bill')
recomendacion2.recommend('Bill')
recomendacion3.recommend('Bill')
recomendacion4.recommend('Bill')

recomendacion1.recommend('Chan')
recomendacion2.recommend('Chan')
recomendacion3.recommend('Chan')
recomendacion4.recommend('Chan')

recomendacion1.recommend('Dan')
recomendacion2.recommend('Dan')
recomendacion3.recommend('Dan')
recomendacion4.recommend('Dan')

recomendacion1.recommend('Hailey')
recomendacion2.recommend('Hailey')
recomendacion3.recommend('Hailey')
recomendacion4.recommend('Hailey')

recomendacion1.recommend('Jordyn')
recomendacion2.recommend('Jordyn')
recomendacion3.recommend('Jordyn')
recomendacion4.recommend('Jordyn')

recomendacion1.recommend('Sam')
recomendacion2.recommend('Sam')
recomendacion3.recommend('Sam')
recomendacion4.recommend('Sam')


recomendacion1.recommend('Veronica')
recomendacion2.recommend('Veronica')
recomendacion3.recommend('Veronica')
recomendacion4.recommend('Veronica')


#recomendacion2.loadBookDB('')
