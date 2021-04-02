# me.hugoify

Produce a [Hugo](https://gohugo.io)/web-ready derived view of the content on [zhehao.me](https://github.com/zhehaowang/zhehao.me).

### How to use

* Set up Hugo
  * `snap`
  * `linuxbrew` / `brew`
* Install dependencies `pip3 install -r requirements.txt`
* Clone submodule `git submodule init; git submodule update`
  * If submodule `checkout` complains, `git rm --cached checkout`
* `./main.py`

optionally,
* update search index
* update p_ google photos (require js edits for now)

### Renewing certificate

* Check out [renew.sh](src/renew.sh)
