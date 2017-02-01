# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 18:02:22 2016

I made this for my dad who teaches English. He wanted a way to
easily divide his 21 students into 5 peer-editing groups, and
then, as many times as possible, switch the groups without having
anyone share a group with a particular person more than once. He
suggested there might be 4 such configurations that I could find
and he would simply repeat them over and over.

It turns out that 4 configurations are not always guaranteed.
So, to minimize repeated pairs, I give each student
a "pairing history," which is easiest to record in an Array
with both axes corresponding to the same list of all the
students. For example, if student 8 appears in the same group
as student 4, then both HistoryArray[4,8] and HistoryArray[8,4]
would increase by one. Minimizing previous pairings in a group
is achieved by first ordering a list of students (Members of the
UnsortedMob) by their row sum in the HistoryArray, then taking
each student from that list and adding it to the group with
the lowest PotentialClashes (pairing history values from the
HistoryArray). Evens and Odds ensure that groups are as
close in size as possible.

Works cited: https://www.jstor.org/stable/822823?seq=1#page_scan_tab_contents

@author: Chris
"""

import numpy as np
from itertools import count
import random

class UnsortedMob(object):
    def __init__(self, Members = None,HistoryArray = None):
        self.SortResult = []
        Group.resetCount()
        Student.resetCount()
        #Input can either be passed in as an argument or requested
        #from the user.
        if Members == None:
            Members = []
            s = 0
            while True:
                NewStudent = Student()
                input_ = input("Please type a name, or press Enter if finished: ")
                if input_ != "":
                    Members.append(NewStudent)
                    Members[s].Name = input_
                    s += 1
                else:
                    break
            self.Members = Members
        else:
            self.Members = Members
        if HistoryArray is None:
            self.HistoryArray = np.zeros((len(self.Members),len(self.Members)))
        else:
            self.HistoryArray = HistoryArray
            print(HistoryArray)
        #self.GroupCount = int(input("How many groups this time? "))
        print("")


    def sort(self):
        Groups = [Group(None) for each in range(self.GroupCount)]
        #A list of students ordered by sum of previous pairings, greatest to least.
        #Now with a randomizer for when the sum is the same.
        r=np.random.random(len(self.Members))
        MobRandomizer = np.lexsort((r,np.sum(self.HistoryArray,axis=0)))[::-1]
        Sorted_Members = list(np.array(self.Members)[MobRandomizer])
        Sorted_Groups = []
        #Evens are the items in the Sorted_Members list that can be
        #evenly divisible into groups with no students left over. Odds
        #are the leftover students and fit in on top of some groups.
        Evens = Sorted_Members[:len(Groups)*(len(Sorted_Members)//len(Groups))]
        Odds = Sorted_Members[len(Groups)*(len(Sorted_Members)//len(Groups)):]
        for M in Evens:
            #Count how many repeated pairings if M is placed in a group
            PotentialClashes = [0]*len(Groups)
            for G in Groups:
                for S in G.Students:
                    PotentialClashes[G.id] += self.HistoryArray[M.id,S.id]
            Sorted_Groups = [G for (C,G) in sorted(zip(PotentialClashes,Groups), key=lambda x: (x[0],random.random()))]
            for G in Sorted_Groups:
                if len(G.Students) < len(self.Members)//len(Groups):
                    G.addStudent(M)
                    #Update the history array
                    for S in G.Students[:-1]:
                        self.HistoryArray[S.id,M.id] += 1
                        self.HistoryArray[M.id,S.id] += 1
                    break
        #A way to make this code less repetitive would be
        #really good! This for loop is almost identical to the one in
        #Evens except it has different restrictions on where Members of
        #the Mob can be placed.
        for M in Odds:
            PotentialClashes = [0]*len(Groups)
            for G in Groups:
                for S in G.Students:
                    PotentialClashes[G.id] += self.HistoryArray[M.id,S.id]
            Sorted_Groups = [G for (C,G) in sorted(zip(PotentialClashes,Groups), key=lambda x: (x[0],random.random()))]
            for G in Sorted_Groups:
                if len(G.Students) < len(self.Members)//len(Groups) + 1:
                    G.addStudent(M)
                    #Update the history array
                    for S in G.Students[:-1]:
                        self.HistoryArray[S.id,M.id] += 1
                        self.HistoryArray[M.id,S.id] += 1
                    break

        #Frames the groups in a nice, polished SortedClass, then
        #prints them all.
        self.SortResult = SortedClass(Groups)
        for G in self.SortResult.Groups:
            print("Group " + str(G.id+1))
            for S in G.Students:
                print(S.Name)
            print("")

class SortedClass(object):
    def __init__(self, Groups = None):
        if Groups is None:
            Groups = []
        self.Groups = Groups

class Group(object):
    _ids = count(0)
    def resetCount():
        Group._ids = count(0)
    def __init__(self, Students = None):
        self.id = next(Group._ids)
        if Students is None:
            self.Students = Students = []
        self.Students = Students
    def addStudent(self, Student):
        self.Students.append(Student)

class Student(object):
    _ids = count(0)
    def resetCount():
        Student._ids = count(0)
    def __init__(self):
        self.id = next(Student._ids)
        self.Name = ""

def main():
    Mob = UnsortedMob()
    print("Group Assignment #1")
    Mob.sort()
    print("----------")
    #Shuffles the groups over and over and over again.
    i = 2
    while True:
        print("Group Assignment #" + str(i) + ".", end = " ")
        NewMob = UnsortedMob(Mob.Members,Mob.HistoryArray / 2)
        NewMob.sort()
        Mob = NewMob
        i+=1
        print("----------")
if __name__ == "__main__":
    main()
