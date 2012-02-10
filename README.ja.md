pyful - Python File Management Utility
======================================

pyfulはLinuxのためのキーボード操作のCUIファイラーです。
このアプリケーションは，xtermなどのターミナルエミュレータ上で動作します。

詳細は，<https://github.com/anmitsu/pyful/wiki>を見てください。

特徴
----

* Pythonによる柔軟で強力なカスタマイズ
* 多画面のファイルビュー
* 対話的なコマンドライン
* zshのようなコマンドライン補完機能
* 高レベルなファイル操作
* Migemo検索に対応

インストール
--------------

pyfulは，以下のコマンドを実行することでインストールすることができます。

    $ git clone git://github.com/anmitsu/pyful
    $ cd pyful
    $ sudo python setup.py install -f
    $ pyful

依存関係
--------

pyfulは，Ubuntu 11.10上のPython2.7およびPython3.2によって動作が確認されています。

日本語をはじめとするマルチバイト文字を正常に表示させるためには，
**libncursesw**ライブラリが必要になる場合があります。

また，pyfulは文字列のエンコーディングが**utf-8**であることを前提にして
動作しています。したがって，**utf-8**以外のエンコーディングを使用している
環境においては正常な動作は期待できません。

設定
----

pyfulの設定は**~/.pyful/rc.py**を編集することによって行います。

rc.pyの設定については，<https://github.com/anmitsu/pyful/wiki/Configuration>を見てください。
