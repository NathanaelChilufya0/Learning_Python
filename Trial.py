msg = 7
msg2 = 'hi'
msg3 = "hello"
#print(msg)

#List
alist=[45,50,"halo",'a']
alist.append(22)
#alist.remove(22)
#alist.extend(range(6,10))
#alist.insert(2,2)
#alist.pop(2) or alist.pop() or  
#alist.remove(45)alist.remove(50)print(alist) alist.sort()
for x in alist:
    if x=='a':
        break
    print(x)
#print(alist[2:4])
n=input()
print(n)

#dictionary
adict={"name":"Nathan"}
#print(adict)
def adding():
    sum=1+1
    return sum
#print(adding())

#Using tuples
x = ('python', 'john',3,5) 
#another approach 
y = 'python' , 'john', '3' 
#print(a[3]+a[2]) 
#slicing next
a = (1,2,3,4,5,6,7,8,9,10) 
b = ('j','j','jk','j2','sj')
#print(alist[-2])
#print(alist[2]) 
#print(a[1:8]); print(a[1:]); print(a[:5])
#print(b.count('j'))    
#print(a.index(5))
print('I can count: ')
#for i in a: print(i,i+1) #how tp print in a straight line?

#print(type(msg3))
#FILE I/O
fo = open("/tmp/python.txt","w")
fo.write("this is line one")
fo.write("this is line two")
fo.close()
fo = open("/tmp/python.txt","r")
str = fo.read(100)
print (str)
#not closing or displaying the required string
fo.close()