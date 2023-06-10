style = """<script src="https://assets.crowd.aws/crowd-html-elements.js" xmlns=""></script>

<style>
    h3 {
        margin-top: 10px;
    }

    crowd-card {
        width: 100%;

    }

    .container {
        display: grid;
        grid-template-columns: 2fr 7fr 1fr;
    }

    .container>div {
        margin: 10px;
    }

    .column {
        display: grid;
        grid-template-columns: auto;
        grid-template-rows: minmax(150px, max-content) auto;
    }

    .card {
        margin: 10px;
        white-space: pre-wrap;
    }

    .radio-box {
        margin-bottom: 20px;
        height: fit-content;
        padding-bottom: 10px;
    }

    .claim {}

    .claim::before {
        content: "Claim: ";
        font-weight: bold;
        color: chocolate;
    }

    .explanation {}

    .explanation:before {
        content: "Explanation: ";
        font-weight: bold;
        color: goldenrod;

    }

    .example {
        margin: 5px;
        background-color: aliceblue;
    }

    .example:before {
        content: "Example: ";
        font-weight: bold;
        font-size: large;
    }

    .article:before {
        content: "Article: ";
        font-weight: bold;
        font-size: large;
        color: cornflowerblue;
    }

    .warning {
        font-weight: bold;
        font-size: larger;
        color: red;
        animation: blinker 1s linear infinite;
    }

    @keyframes blinker {
        0% {
            opacity: 0.33;
        }
    }

    .spoiler,
    .spoiler>* {
        transition: color 0.5s, opacity 0.5s
    }

    .spoiler:not(:hover) {
        color: transparent
    }

    .spoiler:not(:hover)>* {
        opacity: 0
    }

    /* fix weird transitions on Chrome: */
    blockquote,
    blockquote>*:not(a) {
        color: black
    }
</style>

<div id="errorBox"></div>
"""

html = """
<div id="errorBox"></div>
<crowd-form>
    <short-instructions>
        <p>Given the verdict and the claim, try to predict whether the claim is true, false or misleading or whether
            it's hard to judge.</p>

        <p>Once you did, read the article that the verdict summarises, and rate on a scale from 1 to 5, whether
            the verdict is a good summary of the article.</p>
        <p>
            Then, answer all subsequent questions about the summary.
        </p>
        <p>
            Make sure to read the full instructions!
        </p>
        <p>
            You should take around 1.5 minutes per TAB (i.e. going through 6 tabs will take you 9 minutes).
        </p>
    </short-instructions>

        <full-instructions>
        <h2>Instructions</h2>
        <p>
            We are collecting ratings for summaries of fact verification articles to study explainable automated
            fact verification.
        </p>
        <p>
            In this task, you will be asked to judge the quality of (automatically generated) summaries of
            fact verification articles.
        </p>

        <div class="Example">
            <p class="claim">A Pfizer document contains a list of around 158,000 adverse events 'from their
                vaccine'.</p>
            <p class="explanation"> No it doesn't. The document lists a mixture of reported adverse events following
                vaccination. Many may not have been caused by the vaccine.</p>
            <p class="article"> A widely shared article on the Express website about the safety of Pfizer's Covid-19
                vaccine is misleading in several ways.<br />It incorrectly claims that a recently published document
                about adverse events following vaccination is the first time the public have been allowed to see the
                clinical trial data that Pfizer submitted to the US Food and Drug Administration (FDA) for the
                authorisation of the vaccine. In fact, much of the data in this document does not come from Pfizer's
                clinical trials, and some adverse event data from the trials has been publicly available on the FDA
                website at least since December 2020. [...]</p>
        </div>

        <p>You will need to <i>(a)</i> judge, whether the claim is true, based on the verdict only. </p>
        <p>Afterwards, you will need to <i>(b)</i> assign a numeric score from 1 to 5 based on how well you think
            the verdict summarises the full article (where 5 is the best). Then answer some questions to
            rationalise your score and further describe the quality of the summary.

            Note that the full article appears only after you have judged the explanation.</p>

        <p>In judging the (reported) truthfulness of the claim:</p>
        <ul>
            <li>
                please disregard your personal opinion about the claim. It does not matter whether <i>you</i> think
                it's true, but rather what the verdict states.
            </li>
            <li>
                Select <strong>True</strong>, if the verdict states that the claim is true without any caveats.

                <div class="example">
                    <p class='claim' </p>Nigeria ranked third in 2020 Global Terrorism Index.</p>
                    <p class='explanation' </p>Nigeria stays third in global terrorism ranking for fifth year in a row
                    </p>
                </div>
            </li>
            <li>
                Select <strong>Mostly</strong>, if the verdict states that the claim is true but there are some
                lacking information or imprecisions.

                <div class="example">
                    <p class='claim' </p>You've got thousands of people serving in the military who are transgender.</p>
                    <p class='explanation'>There are no solid numbers from the Defense Department, but two sources have
                        provided
                        recent estimates extrapolated from survey and insurance data. One 2014 UCLA brief estimated as
                        many as
                        15,500 active duty and reserve service members may identify as transgender.
                        A 2016 RAND Corp. study commissioned by the Pentagon suggested between
                        2,150 and 10,790 active and reserve duty troops.</p>
                    </p>
                </div>
            </li>
            <li>
                Select <strong>Half/Half</strong>, if the verdict states that the claim is a mixture of correct and
                false
                information, for example when there are two parts to the claim but only one is correct.
                <div class="example">
                    <p class='claim' </p>Australian military bases being renamed to ‘Aboriginal place names’ and the
                        Australian flag downgraded on Defence publications.</p>
                    <p class='explanation'>Australia’s military bases will retain their existing English names - their
                        Aboriginal names will be added. </p>
                </div>
            </li>
            <li>
                Select <strong>Mostly False</strong>, if the verdict states that the claim is mostly false, for example
                when it
                is based on something that is true in principle but draws the wrong conclusions.
                <div class="example">
                    <p class='claim' </p>There are 1,600 new coal-fired power plants being constructed as I speak around
                        the world.</p>
                    <p class='explanation'>A New York Times article from more than two years ago cited the 1,600 figure,
                        but even then it described units being "planned or under construction" -- not strictly under
                        construction.
                        In addition, those numbers appear to have shrunk in the succeeding two years. Using the same
                        website as the Times used, there are 458 coal-fired units being built worldwide today, and 903
                        if you include those in the pre-permitting or permit phase - significantly less than what
                        Roberts indicated. </p>
                </div>
            </li>
            <li>
                Select <strong>False</strong>, if the verdict clearly states that the claim is false, incorrect, made up
                etc.
                <div class="example">
                    <p class='claim' </p>Antifa is planning a flag burning ceremony at Gettysburg National Ceremony on
                        July 4.</p>
                    <p class='explanation'>Antifa July 4th plot unproven, say police.</p>
                </div>

            </li>
            <li>
                Select <strong>Misleading</strong>, if the verdict states that the claim is misleading. This is the case
                when the claim describes something that happened in principle (e.g. someone said something) but takes it
                out of context, exaggerates it, attributes it to a wrong person, etc.
            </li>
            <li>
                Select <strong>Satire</strong>, if the verdict states that the claim is clearly satire, for example as
                it could originate satirical news outlets, such as "The Onion".




            </li>
            <div class="example">
                <p class='claim'>Korean newscaster bursts out laughing while reporting China motorcycle ban.</p>
                <p class='explanation'> Satirical video about China's motorcycle restrictions is doctored from Korean TV
                    advert.</p>
            </div>
            <li>
                If you think the verdict falls into multiple categories, please select the one you think is most
                appropriate.
            </li>
            <li>
                If the verdict doesn't fall into any of the categories above, select "Hard to say".
            </li>
        </ul>

        <p>In judging the quality,</p>
        <ul>
            <li>
                When rating the quality of the summary, give the highest mark (5) when you <strong>cannot think of a way
                    to improve</strong> the summary. Give the lowest mark (1) if the summary is
                <strong>unrelated</strong>
                to the article. For ratings in between, consider the following:
                Does the summary capture the <strong>main idea</strong> of the article?
            </li> See also more examples below.

            <li>
                For the question <strong>Does the summary contradict the article?</strong> select <strong>yes</strong>
                if the summary <strong>clearly contradicts</strong> the article. For example, if the article
                says <i>"...some of the chemicals listed are present in vaccines..."</i> and the summary reads
                <i>"None of the chemicals listed are present in vaccines."</i>
            </li>
            <li>
                For the question <strong>Does the summary contradict itself?</strong> select <strong>yes</strong>
                if the summary <strong>clearly contradicts</strong> itself. For example, if the explanation reads
                <i>"This is based on military spending, not military spending."</i>.
            </li>
            <li>
                For the question <strong>Is there any new information in the summary which does not appear in the
                    article?</strong> select <strong>yes</strong>
                if the summary <strong>invents</strong> new information. For example, if the explanation reads
                <i>"This is not true. The majority of immigrants who speak no English arrived in the UK as
                    grandparents."</i>
                but the article does not mention grandparents at all.
            </li>
            <li>
                Finally, For the question <strong>Would you use this summary as part of an argument to convince an
                    opposing party about the claim's verdict?</strong> select <strong>yes</strong>
                if you would use the summary <strong>"as-is"</strong> (i.e. copy-pasting it) in an online debate, to
                <strong>support</strong> the verdict of the claim.
                Note, that this does not have to reflect your stance on the claim, but rather whether you find if the
                summary <strong>explains</strong>
                the verdict <strong>convincingly</strong>.
            </li>
        </ul>
        <h3>More examples for judging the main idea (1-5 scale)</h3>
        <div class="Example"> 5/5.
            <p class="explanation">Trace amounts of this antibiotic may end up in certain vaccines. If you are allergic
                to it could cause an allergic reaction.</p>
            <p class="article">Note: the information in this article refers to vaccines in the UK, unless otherwise
                stated.<br />
                A picture claiming to list vaccine ingredients and health problems they'e linked to has been shared on
                Facebook.<br />
                'None of these should be injected into your body'. <br />
                Facebook user, 19 February 2019
                <br /> Although some of the chemicals listed are present in vaccines, or are used in their production,
                none are at high enough levels in vaccines to do harm. If you have a serious allergy to something like
                latex or certain antibiotics, vaccines containing those chemicals may cause a serious reaction. Someone
                with an allergy would also get this reaction if they used a latex product, or were put on that specific
                antibiotic for the first time.
                <br />Some of the health issues listed in the image have been observed in studies using animals, or have
                known side-effects in humans. But this is only in much higher concentrations than would ever be present
                in vaccines.[...]
            </p>
        </div>

        <div class="Example"> 4/5. Omits the fact that traces might be present and could case an allergic reaction.
            <p class="explanation">This isn’t in any UK vaccines. It’s in many vaccines, and there’s no evidence it can
                cause any of these.</p>
            <p class="article">Note: the information in this article refers to vaccines in the UK, unless otherwise
                stated.<br />
                A picture claiming to list vaccine ingredients and health problems they'e linked to has been shared on
                Facebook.<br />
                'None of these should be injected into your body'. <br />
                Facebook user, 19 February 2019
                <br /> Although some of the chemicals listed are present in vaccines, or are used in their production,
                none are at high enough levels in vaccines to do harm. If you have a serious allergy to something like
                latex or certain antibiotics, vaccines containing those chemicals may cause a serious reaction. Someone
                with an allergy would also get this reaction if they used a latex product, or were put on that specific
                antibiotic for the first time.
                <br />Some of the health issues listed in the image have been observed in studies using animals, or have
                known side-effects in humans. But this is only in much higher concentrations than would ever be present
                in vaccines. [...]
            </p>
        </div>

        <div class="Example"> 3/5. The main point is not well captured and the statement is rather general.
            <p class="explanation">Neomycin sulphate is in some vaccines, but is not in all.</p>
            <p class="article">Note: the information in this article refers to vaccines in the UK, unless otherwise
                stated.<br />
                A picture claiming to list vaccine ingredients and health problems they'e linked to has been shared on
                Facebook.<br />
                'None of these should be injected into your body'. <br />
                Facebook user, 19 February 2019
                <br /> Although some of the chemicals listed are present in vaccines, or are used in their production,
                none are at high enough levels in vaccines to do harm. If you have a serious allergy to something like
                latex or certain antibiotics, vaccines containing those chemicals may cause a serious reaction. Someone
                with an allergy would also get this reaction if they used a latex product, or were put on that specific
                antibiotic for the first time.
                <br />Some of the health issues listed in the image have been observed in studies using animals, or have
                known side-effects in humans. But this is only in much higher concentrations than would ever be present
                in vaccines.[...]
            </p>
        </div>

        <div class="Example"> 2/5. Misrepresentation of the article, but not completely unrelated.
            <p class="explanation">If you are allergic to it, vaccine could cause an allergic reaction.</p>
            <p class="article">Note: the information in this article refers to vaccines in the UK, unless otherwise
                stated.<br />
                A picture claiming to list vaccine ingredients and health problems they'e linked to has been shared on
                Facebook.<br />
                'None of these should be injected into your body'. <br />
                Facebook user, 19 February 2019
                <br /> Although some of the chemicals listed are present in vaccines, or are used in their production,
                none are at high enough levels in vaccines to do harm. If you have a serious allergy to something like
                latex or certain antibiotics, vaccines containing those chemicals may cause a serious reaction. Someone
                with an allergy would also get this reaction if they used a latex product, or were put on that specific
                antibiotic for the first time.
                <br />Some of the health issues listed in the image have been observed in studies using animals, or have
                known side-effects in humans. But this is only in much higher concentrations than would ever be present
                in vaccines.[...]
            </p>
        </div>

        <div class="Example"> 1/5. Completely unrelated explanation.
            <p class="explanation">The page claiming this is not affiliated with Waitrose and there is no prize.</p>
            <p class="article">Note: the information in this article refers to vaccines in the UK, unless otherwise
                stated.<br />
                A picture claiming to list vaccine ingredients and health problems they'e linked to has been shared on
                Facebook.<br />
                'None of these should be injected into your body'. <br />
                Facebook user, 19 February 2019
                <br /> Although some of the chemicals listed are present in vaccines, or are used in their production,
                none are at high enough levels in vaccines to do harm. If you have a serious allergy to something like
                latex or certain antibiotics, vaccines containing those chemicals may cause a serious reaction. Someone
                with an allergy would also get this reaction if they used a latex product, or were put on that specific
                antibiotic for the first time.
                <br />Some of the health issues listed in the image have been observed in studies using animals, or have
                known side-effects in humans. But this is only in much higher concentrations than would ever be present
                in vaccines. [...]
            </p>
        </div>
    </full-instructions>

    <crowd-tabs id="crowd-tabs">
    {}
    </crowd-tabs>
</crowd-form>"""

functions = """<script>
    function reset(i) {
        document
            .getElementById("firstForm" + i)
            .querySelectorAll('input[name="rate"]').forEach((e) => e.checked = false);
        document
            .getElementById("firstForm" + i)
            .querySelectorAll('input[name="verdict"]').forEach((e) => e.checked = false);
        document.getElementById("right" + i).style = 'display: none;';
    }

    function uncoverSecondPart(i) {
        document.getElementById("right" + i).style = '';
    }

    document.addEventListener('all-crowd-elements-ready', () => {
        for (let i = 1; i <= 10; i++) {
            document.getElementById('firstForm' + i).addEventListener("click", function (event) {
                if (event.target && event.target.matches("input[type='radio']")) {
                    uncoverSecondPart(i);
                }
            });
        }

        let hasSubmitted = false;

        document.querySelector('crowd-form').onsubmit = function (event) {
            errorBox.innerHTML = '';
            let allChecked = makingSureChecked();
            console.log(event);
            console.log("is all checked?" + allChecked);
            if (!allChecked.every(elem => !!elem)) {
                event.preventDefault();
                let i = 1;
                let errors = [];
                allChecked.forEach(function (elem) {
                    if (elem === false) {
                        console.log(event);
                        console.log(errorBox);
                        errors.push("Please assign a rating to items in Tab " + i + "!");
                    }
                    i++;
                })
                errorBox.innerHTML = "<crowd-alert type='error'>" + errors.join('<br/>') + "</crowd-alert>";
                errorBox.scrollIntoView();
                return
            }

        };
        const params = new URLSearchParams(window.location.search);


        function makingSureChecked() {
            let result = [];
            for (let j = 1; j <= 10; j++) {
                const rates = document
                    .getElementById("tab" + j)
                    .querySelectorAll('input[name="rate' + j + '"]');
                const verdicts = document
                    .getElementById("tab" + j)
                    .querySelectorAll('input[name="verdict' + j + '"]');
                let rate_flag = false;
                let verdict_flag = false;
                for (let i = 0; i < rates.length; i++) {
                    if (rates[i].checked) {
                        rate_flag = true;
                        break;
                    }
                }
                for (let i = 0; i < verdicts.length; i++) {
                    if (verdicts[i].checked) {
                        verdict_flag = true;
                        break;
                    }
                }
                result.push(rate_flag && verdict_flag);
            }
            return result;
        }
    });

</script>
"""


def render(i):
    return f"""
    <crowd-tab header="Tab {i}" id="tab{i}" class="container">
    <div className='column' id="left{i}">
        <div>
            <h3>Claim</h3>
            <crowd-card>
                <div className="card">${{claim{i}}}</div>
            </crowd-card>
            <h3>Verdict</h3>
            <crowd-card>
                <div className="card">${{verdict{i}}}</div>
            </crowd-card>
        </div>
        <span onClick="reset({i});">Reset</span>
        <div className="radio-box" id="firstForm{i}">
            <h3>Looking at the verdict only, the claim is</h3>
            <table>
                <tr>
                    <td>
                        <input type="radio" id="true{i}" name="verdict{i}" value="true"><label htmlFor="true{i}">True</label>
                    </td>
                    <td>
                        <input type="radio" id="almost{i}" name="verdict{i}" value="almost"><label htmlFor="almost{i}">Mostly
                            True</label>
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="radio" id="half{i}" name="verdict{i}" value="half"><label htmlFor="half{i}">Half/Half</label>
                    </td>
                    <td>
                        <input type="radio" id="hardly{i}" name="verdict{i}" value="hardly"><label htmlFor="hardly{i}">Mostly
                            False</label>
                    </td>
                </tr>
                <tr>
                    <td><input type="radio" id="false{i}" name="verdict{i}" value="false"><label htmlFor="false{i}">False</label>
                    </td>
                    <td><input type="radio" id="satire{i}" name="verdict{i}" value="satire"><label htmlFor="satire{i}">Satire</label></td>
                </tr>
                <tr>
                    <td><input type="radio" id="unk{i}" name="verdict{i}" value="unk"><label htmlFor="un{i}">Hard to say</label>
                    </td>
                </tr>
            </table>
        </div>
    </div>

    <div className='column' id="right{i}" style="display: none">
        <div>
            <h3>Summary</h3>
            <crowd-card>
                <div className="card">
                    ${{verdict{i}}}
                </div>
            </crowd-card>
        </div>
        <div>
            <h3>Article</h3>
            <crowd-card>
                <div className='card'>
                    <div className="card">${{text{i}}}</div>
                </div>
            </crowd-card>
        </div>
        <div className="radio-box">
            <h3>How well does the summary capture the main idea of the article?</h3>
            <input type="radio" id="rate0{i}" name="rate{i}" value="1"><label htmlFor="rate0{i}">1</label>
            <input type="radio" id="rate1{i}" name="rate{i}" value="2"><label htmlFor="rate1{i}">2</label>
             <input type="radio" id="rate2{i}" name="rate{i}" value="3"><label htmlFor="rate0{i}">3</label>
            <input type="radio" id="rate3{i}" name="rate{i}" value="4"><label htmlFor="rate1{i}">4</label>
             <input type="radio" id="rate4{i}" name="rate{i}" value="5"><label htmlFor="rate0{i}">5</label>
        </div>
        <div className="radio-box">
            <h3>Does the summary contradict the article?</h3>
            <input type="radio" id="contra-article0{i}" name="contra-article{i}" value="1"><label htmlFor="contra-article0{i}">yes</label>
            <input type="radio" id="contra-article1{i}" name="contra-article{i}" value="2"><label htmlFor="contra-article1{i}">no</label>

        </div>
        <div className="radio-box">
            <h3>Does the summary contradict itself?</h3>
            <input type="radio" id="contra-self0{i}" name="contra-self{i}" value="1"><label htmlFor="contra-self0{i}">yes</label>
            <input type="radio" id="contra-self1{i}" name="contra-self{i}" value="2"><label htmlFor="contra-self1{i}">no</label>

        </div>
        <div className="radio-box">
            <h3>Is there any new information in the summary which does not appear in the article?</h3>
            <input type="radio" id="new0{i}" name="new{i}" value="1"><label htmlFor="new0{i}">yes</label>
            <input type="radio" id="new1{i}" name="new{i}" value="2"><label htmlFor="new1{i}">no</label>
        </div>
        <div className="radio-box">
            <h3>Would you use this summary as part of an argument to convince an opposing party about the claim's verdict?</h3>
            <input type="radio" id="convince0{i}" name="convince{i}" value="1"><label htmlFor="convince0{i}">yes</label>
            <input type="radio" id="convince1{i}" name="convince{i}" value="2"><label htmlFor="convince1{i}">no</label>
        </div>
        
    </div>
</crowd-tab>
"""


if __name__ == '__main__':
    tabs = [render(i) for i in range(1, 2)]
    print(style + html.format('\n'.join(tabs)) + functions)