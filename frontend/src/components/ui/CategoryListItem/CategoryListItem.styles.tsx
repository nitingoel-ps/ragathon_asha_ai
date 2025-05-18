import styled from "styled-components";

const StyledCategoryListItem = styled.div`
    .categoryItemHeader{
        display: flex;
        height: fit-content;
        justify-content: space-between;
        margin-bottom: 10px;
        align-items: flex-end;
        h2{
            margin-bottom: 0;
        }
        p {
            margin-bottom: 0;
            color: ${(props) => props.theme.colors.text.tertiary};
        }
    }
`

export default StyledCategoryListItem