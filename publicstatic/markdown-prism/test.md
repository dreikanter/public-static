~~~ ruby
p "Hello!"
~~~

Usage example for short language designation:

~~~ py
class CodeBlockExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """Add CodeBlockPreprocessor to the Markdown parser."""
        md.registerExtension(self)
        proc = CodeBlockPreprocessor(md)
        md.preprocessors.add('code_block', proc, ">normalize_whitespace")
~~~

More examples:

~~~ bash
echo Hello!
~~~

Undefined language:

~~~
#include <stdio>

void main()
{
    cout << "Hello!";
}
~~~
