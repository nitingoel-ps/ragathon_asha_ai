import styled from "styled-components";

const StyledCategoryListItem = styled.div`
    .categoryItemHeader{
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        p {
            color: ${(props) => props.theme.colors.text.tertiary};
        }
    }
`

export default StyledCategoryListItem