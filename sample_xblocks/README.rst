Demo XBlocks
============

This package contains some sample XBlocks to illustrate the capabilities of
the XBlock specification. The following blocks are included:

  * **basic.content:HelloWorldBlock** A block which simply displays the text "Hello World"

  * **basic.content:AllScopesBlock** A block which demonstrates the scopes that come built in with XBlock

  * **basic.content:HtmlBlock** A block which displays a specified block of HTML text

  * **basic.structure:Sequence** A container block which displays its children in a tabbed layout

  * **basic.structure:VerticalBlock** A container block which displays its children in a vertical list

  * **basic.structure:SidebarBlock** A variant of the vertical block

  * **basic.problem:ProblemBlock** A block which presents a problem and grades student responses

  * **basic.problem:TextInputBlock** 

  * **basic.problem:EqualityCheckerBlock** 

  * **basic.problem:AttemptScoreboardBlock** 

  * **basic.slider:Slider** A block which presents a slider and remembers the student's setting

  * **basic.view_counter:ViewCounter** 

  * **basic.thumbs:ThumbsBlock** A block which shows the total number of times it has been viewed

  * **basic.filethumbs:FileThumbsBlock** 

Each of these blocks can be referenced in scenarios using a keyword in XML that is specified in the "entry_points" attribute of the setup tuple. 