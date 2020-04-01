# 2020_03_24

## 구현한 것
latest_post를 긁어와서 latest.txt file 과 비교해서 그 값이 다른경우 메일로 뿌려줌.
현재 첨부파일의 형식으로 보내지는 못하고, 링크를 직접 전달해줌.
크론탭을 활용하여 아침 9시부터 저녁 8시까지 3분마다 함수를 실행시켜 공지를 전달해줌.

## 구현해야 할 것
현재 3분마다 request 를 요청하는 비용이 너무 큼.
또한 이 3분 동안 여러 게시글이 올라오는 경우 모든 경우를 fetch 하기는 어려움.
조금 더 함수화를 진행하여 규격화할 필요성이 있음.
첨부파일의 형태로 파일을 전송하기 위해서는 어떤 방법을 취해야할까? 파일을 직접 다운바도 이걸읽어 내는 방식을 사용해야 되나?
파이썬에서의 전역 변수에 대한 생각 정리
또한 만약 이 크론이 죽는경우 해결책에 대해 강구해야 함.Docker self-healing can solve this problem


# 2020_04_01
My nuc has gone. So I have to check directly. The /tmp file became read only file. I think that nuc has some technical issue. I have to make to git to prevent this happen again.
Change corntab 9-22.
And I found that my cron shows error, but I don't have any way to check it. Now I found the way to remain log.

/etc/rsyslog.d/50-defualt.conf

Find a line
#cron.* -> uncomment it

sudo service rsyslog restart

and then my log will be shown in /var/log/cron.log
