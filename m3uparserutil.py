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
    def parseM3U(self,infile,serverurl,ottkey):
        #inf = open(infile,'r')
        xbmc.log(msg='m3uparse: open file:', level=xbmc.LOGDEBUG)
        inf = infile
    
        # # # all m3u files should start with this line:
        #EXTM3U
        # this is not a valid M3U and we should stop..
        line = inf.readline()
        xbmc.log(msg='m3uparse: firstline:'+str(line), level=xbmc.LOGDEBUG)
        # initialize playlist variables before reading file
        playlist=[]
        if '#EXTM3U' not in line:
            #line.startswith('#EXTM3U'):
            xbmc.log(msg='m3uparse: return wird ausgeloesst:', level=xbmc.LOGDEBUG)
            return       
        xbmc.log(msg=str('m3uparse: get logos from : '+str(serverurl)+'/api/channel_now.jsonp'), level=xbmc.LOGDEBUG)
        logos=self.getOTTLogos(serverurl+'/api/channel_now.jsonp')
        xbmc.log(msg='m3uparse: logo:'+str(logos), level=xbmc.LOGDEBUG)
        song=Track(None,None,None,None,None,None,None)
        chid=20000
        for line in inf:
            line=line.strip()
            #xbmc.log(msg='m3uparse: line:'+str(line), level=xbmc.LOGDEBUG)
            if line.startswith('#EXTINF:'):
                # pull length and title from #EXTINF line
                length,title=line.split('#EXTINF:')[1].split(',',1)
                xbmc.log(msg='m3uparse: title:'+str(title), level=xbmc.LOGDEBUG)
                xbmc.log(msg='m3uparse: length:'+str(length), level=xbmc.LOGDEBUG)
                # title=title.decode('UTF-8')
                song=Track(length,title,None,None,None,None,None)
                xbmc.log(msg='m3uparse: Track saved with length and title', level=xbmc.LOGDEBUG)
            elif (len(line) != 0):
                xbmc.log(msg='m3uparse: add element to Playlist', level=xbmc.LOGDEBUG)
                # pull song path from all other, non-blank lines
                #song.path=line
                #xbmc.log(msg='m3uparse: ottkey: '+ottkey, level=xbmc.LOGDEBUG)
                song.path=self.replaceOTTKey(line,ottkey)
                xbmc.log(msg='m3uparse: add element-url: '+song.path, level=xbmc.LOGDEBUG)
                playlist.append(song)
                lastslash=song.path.rfind('/')
                lastpoint=song.path.rfind('.')
                song.chottid=song.path[lastslash+1:lastpoint:]
                xbmc.log(msg='m3uparse: playlist element shottid:'+str(song.chottid), level=xbmc.LOGDEBUG)
                chid+=1
                song.chid=chid
                xbmc.log(msg='m3uparse: playlist element serverurl: '+serverurl, level=xbmc.LOGDEBUG)
                song.serverurl=serverurl
                try:
                    song.logo=song.serverurl+'/images/'+logos[song.chottid]['img']
                    xbmc.log(msg='m3uparse: playlist element logo: '+song.serverurl+'/images/'+logos[song.chottid]['img'], level=xbmc.LOGDEBUG)
                except:
                    song.logo='https://upload.wikimedia.org/wikipedia/en/c/c6/TV_Guide_logo_2016.png' 
                    xbmc.log(msg='m3uparse: playlist element logo: FALLBACK_LOGO', level=xbmc.LOGDEBUG)
                # reset the song variable so it doesn't use the same EXTINF more than once
                song=Track(None,None,None,None,None,None,None)
                xbmc.log(msg='m3uparse: Track saved with length and title', level=xbmc.LOGDEBUG)
    
        inf.close()
    
        return playlist

    def replaceOTTKey(self,oldpath,newOTTKey):
        parts= oldpath.split('/')
#        print 'PARTTTTTTT 0:'+parts[0]
#        print 'PARTTTTTTT 1:'+parts[1]
#        print 'PARTTTTTTT 2:'+parts[2]
#        print 'PARTTTTTTT 3:'+parts[3]
#        print 'PARTTTTTTT 4:'+parts[4]
#        print 'PARTTTTTTT 5:'+parts[5]
        if len(parts)==6:
            return parts[0]+'//'+parts[2]+'/'+parts[3]+'/'+newOTTKey+'/'+parts[5]
        else:
            return oldpath

# for now, just pull the track info and print it onscreen
# get the M3U file path from the first command line argument
#def main():
#    m3ufile=sys.argv[1]
#    playlist = M3UParser.parseM3U(m3ufile)
#    for track in playlist:
#        print (track.title, track.length, track.path)

#if __name__ == '__main__':
#    main()