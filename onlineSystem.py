
from amazon.api import AmazonAPI
from time import sleep


AMAZON_ASSOC_TAG="xxx"
AMAZON_ACCESS_KEY="xxx"
AMAZON_SECRET_KEY="xxx+GsFu"
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)


exec(open("searchRecommender.py").read())
exec(open("SVDrecommender.py").read())
exec(open("clustersRecommender.py").read())




def recommendBooks(isbnList):
        
    cnt=0
    for isbn in isbnList:
        cnt+=1
        if cnt==10: break
        sleep(1.5)
        try:
            result = amazon.lookup(ItemId=isbn, IdType='ISBN', SearchIndex='Books')
            try:res=result[0]
            except: res=result
            print("Title: ",res.title)
            print("Author: ",res.author)
            print("ISBN: ",res.isbn)
            try: print("Price: ", res.price_and_currency[0]," ",res.price_and_currency[1])
            except: pass
            print("")
            print("")
        except Exception as e:
            #print(str(e))
            pass

            
if __name__ == "__main__":
    
    print("Content-based recommendation...")
    print("Recommendation by ISBN")
    print("")

    isbnList="0553297988 0553560719 0345307674"# Star Wars
    isbnList=findContentbyIsbn(isbnList,0.1)
    recommendBooks(isbnList);
    print("")
    print("-----------------------------------------")
    print("")
    print("Recommendation by title, author...")
    print("")
    keywords="lord of the rings"
    isbnList=findContentByKeywords(keywords,0.15)
    recommendBooks(isbnList);
    print("")
    print("-----------------------------------------")
    print("")
    print("")
    print("Recommendation by low rank matrix approximation")
    print("")
    print("")
    low_rank_matrix=doCV(ratings,epochs=15,cvRounds=1) 
    print("")
    print("")
    user_1=42
    user_2=253
    print("Books recommended for user: ",user_1)
    print("")
    print("")
    recommendBooks(recommendForUser(low_rank_matrix,user_1) );
    print("")
    print("")
    print("Books recommended for user: ",user_2)
    print("")
    print("")
    recommendBooks(recommendForUser(low_rank_matrix,user_1) );
    print("")
    print("")
    print("-----------------------------------------")
    print("")
    print("Recommendation by Clustering (poor performance)")
    print("")
    isbnList="044661162X 1581345283 044022330X 1573221937"
    clusters=findClusters(isbnList)
    for clst in (clusters):
        recommendBooks(set(clst));

#[method for method in dir(result) ]
