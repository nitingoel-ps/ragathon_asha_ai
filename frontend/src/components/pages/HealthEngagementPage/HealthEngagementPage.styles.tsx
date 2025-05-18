import styled from 'styled-components';

export const StyledHealthEngagementPage = styled.div`
    /* constrain to mobile sizing */
    position: relative;
    max-width: 400px;
    width: 100%;
    margin: auto;
    background-color: ${(props) => props.theme.colors.background};
    max-height: 900px;
    
    overflow-y: scroll;
    .mainContent{
        padding-inline: 15px;
        padding-top: 60px;
        padding-bottom: 100px;
    }
    .scoreCard{
        display: grid;
        grid-template-columns: 1.2fr 2fr;
        align-items: center;
        gap: 20px;
        margin-block: 20px;
        h1{
            margin-bottom: .6rem;
        }
        p{
            margin-bottom: 0;
        }
        .highlight {
            color: ${(props) => props.theme.colors.primary};
        }
    }
    .fullWidthImage {

     
    }
    .fullWidthImage{
        max-width: 400px;
        width: 100%;
        //left: 50%;
        //transform: translateX(-50%);
        z-index: ${(props) => props.theme.zIndex.sticky};
        position: sticky;
        &#header{
            top: 0;
        }
        &#footer{
            bottom: 0;
            
        }
    }
`