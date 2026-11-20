interface Props {
    onPrev: () => void;
    }

    const StepCustom = ({ onPrev }: Props) => {
    return (
        <div>
        <h2>직접 입력해주세요</h2>

        <textarea
            placeholder="원하시는 이야기를 적어주세요"
            style={{ width: "100%", height: 100 }}
        />

        <div style={{ marginTop: 30 }}>
            <button onClick={onPrev}>이전</button>
            <button style={{ marginLeft: 10 }}>
            완료
            </button>
        </div>
        </div>
    );
};

export default StepCustom;