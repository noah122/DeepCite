from bs4 import BeautifulSoup
import requests
import tokenizer
import sys
import io

class Claim:
    def __init__(self, href, text, height, parent):
        maxheight = 0 # TODO: iteration 2 problem
        super(Claim, self).__init__()
        # hrefs : several reference links, which is a list of str
        # text : the text of the claim
        # child: a list of claims
        # score: matching score computed by nlp algorithm. Will be edited by user response.
        # parent: a instance of Claim class.
        # visited: a list to store all the hrefs for cycle detection.
        self.href = href
        self.text = text
        self.parent = parent
        self.child = []
        self.height = height
        self.leaf = {}
        self.visited = []
        self.cand, self.score = self.parse_child(maxheight)
        
        # self.branch = order
        # default value of score is 0

    def parse_child(self, maxheight):
        if self.parent != None:
            self.visited = self.parent.visited
        ref2text = {}
        if self.href[:5] != "https" and self.parent != None:
            preref = "https://" + self.parent.href.split('/')[2]
            print(preref)
            self.href = "".join([preref, self.href])
        # Cycle Detection
        if self.href in self.visited:
            # Terminate the scraper and parse the parent node to the leaf list
            self.leaf[self.parent.texts[0]] = self.parent.scores[0]
            return self.parent.texts[0], self.parent.scores[0]
        response = requests.get(self.href)
        self.visited.append(self.href)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_raw = soup.findAll('p')
        # Exception that the child of one claim has no valid sentences, then add its parent to the leaf list.
        if len(text_raw) < 5:
            # Terminate the scraper and parse the parent node to the leaf list
            self.leaf[self.parent.texts[0]] = self.parent.scores[0]
            return self.parent.texts[0], self.parent.scores[0]
        for unit in text_raw:
            if len(unit.findAll('a')) > 0:
                for ref in unit.findAll('a'):
                    ref2text[unit.text] = ref['href']
            else:
                ref2text [unit.text] = ""
        cand = tokenizer.predict(self.text, list(ref2text.keys()), 1)
        texts = [] 
        scores = []
        for text in cand:
            try:
                if ref2text[text[1]] != "" and self.height < maxheight:
                    print(ref2text[text[1]])
                    self.child.append(Claim(ref2text[text[1]], text[1], (self.height + 1), self))
            except KeyError:
                ref_key = ""
                for key in ref2text.keys():
                    if text[1] in key:
                        ref_key = key
                        break
                print(ref2text[ref_key])
                if ref2text[ref_key] != "" and self.height < maxheight:
                    texts.append(text[1])
                    scores.append(text[2])
                    self.child.append(Claim(ref2text[text[1]], text[1], (self.height +1), self))
                elif ref2text[ref_key] == "":
                    self.leaf[text[1]] = text[2]
            
        return texts, scores


    def __repr__(self):
        return "claim: " + self.text + "leaves of the citation tree: " + self.leaf

if "__main__":
    
    url = "http://math.ucr.edu/home/baez/physics/Relativity/GR/grav_speed.html"
    text = "Gravity moves at the Speed of Light and is not Instantaneous. If the Sun were to disappear, we would continue our elliptical orbit for an additional 8 minutes and 20 seconds, the same time it would take us to stop seeing the light (according to General Relativity)."
    root = Claim(url, text, 0, None)




        
