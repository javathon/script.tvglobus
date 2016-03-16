# more info on the M3U file format available here:
# http://n4k3d.com/the-m3u-file-format/

import sys
import urllib2
import StringIO
import json
import xbmc

class Track:
    def __init__(self, length, title, path, chid, chottid, logo, serverurl):
        self.length = length
        self.title = title
        self.path = path
        self.chid = chid
        self.chottid = chottid
        self.logo=logo
        self.serverurl=serverurl

class OTTLogo:
    def __init__(self, chottid, logopath):
        self.logopath = logopath
        self.chottid = chottid
        
class M3UParser:
    
    def getOTTLogos(self,logourl):
        response = urllib2.urlopen(logourl)
        #jsondata=json.loads(response.channel_now)
        
        logojson = StringIO.StringIO()
        logojson.write(response.read())
        logojson.seek(0)
        response.close()
        #js=logojson.read().split("(")[1].strip(")")
        js=logojson.read()
        js=js[js.find('(')+1:].rstrip()[:-1]

        return json.loads(js)
    
    # # # song info lines are formatted like:
    #EXTINF:419,Alice In Chains - Rotten Apple
    # length (seconds)
    # Song title
    # # # file name - relative or absolute path of file
    # ..\Minus The Bear - Planet of Ice\Minus The Bear_Planet of Ice_01_Burying Luck.mp3
    def parseM3U(self,infile,serverurl):
        #inf = open(infile,'r')
        xbmc.log(msg='m3uparse: open file:', level=xbmc.LOGDEBUG)
        inf = infile
    
        # # # all m3u files should start with this line:
            #EXTM3U
        # this is not a valid M3U and we should stop..
        line = inf.readline()
        xbmc.log(msg='m3uparse: firstline:'+str(line), level=xbmc.LOGDEBUG)
        if '#EXTM3U' not in line:
            #line.startswith('#EXTM3U'):
            xbmc.log(msg='m3uparse: return wird ausgeloesst:', level=xbmc.LOGDEBUG)
            return       
        logos=self.getOTTLogos(serverurl+'/api/channel_now.jsonp')
        xbmc.log(msg='m3uparse: logo:'+str(logos), level=xbmc.LOGDEBUG)
        # initialize playlist variables before reading file
        playlist=[]
        song=Track(None,None,None,None,None,None,None)
        chid=20000
        for line in inf:
            line=line.strip()
            xbmc.log(msg='m3uparse: line:'+str(line), level=xbmc.LOGDEBUG)
            if line.startswith('#EXTINF:'):
                # pull length and title from #EXTINF line
                length,title=line.split('#EXTINF:')[1].split(',',1)
                xbmc.log(msg='m3uparse: title:'+str(title), level=xbmc.LOGDEBUG)
                xbmc.log(msg='m3uparse: length:'+str(length), level=xbmc.LOGDEBUG)
                # title=title.decode('UTF-8')
                song=Track(length,title,None,None,None,None,None)
                
            elif (len(line) != 0):
                # pull song path from all other, non-blank lines
                song.path=line
                playlist.append(song)

                lastslash=song.path.rfind('/')
                lastpoint=song.path.rfind('.')
                song.chottid=song.path[lastslash+1:lastpoint:]
                chid+=1
                song.chid=chid
                song.serverurl=serverurl
                song.logo=song.serverurl+'/images/'+logos[song.chottid]['img']
                # reset the song variable so it doesn't use the same EXTINF more than once
                song=Track(None,None,None,None,None,None,None)
    
        inf.close()
    
        return playlist

# for now, just pull the track info and print it onscreen
# get the M3U file path from the first command line argument
#def main():
#    m3ufile=sys.argv[1]
#    playlist = M3UParser.parseM3U(m3ufile)
#    for track in playlist:
#        print (track.title, track.length, track.path)

#if __name__ == '__main__':
#    main()