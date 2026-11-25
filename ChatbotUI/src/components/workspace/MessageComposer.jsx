import { FaImage, FaPaperclip, FaPaperPlane } from "react-icons/fa6";

const MessageComposer = ({ value, onChange, onSubmit, isLoading }) => {
	const canSend = value.trim().length > 0 && !isLoading;

	const handleKeyDown = (event) => {
		if (event.key === "Enter" && !event.shiftKey) {
			event.preventDefault();
			onSubmit();
		}
	};

	return (
		<form
			onSubmit={(event) => {
				event.preventDefault();
				onSubmit();
			}}
			className="shrink-0 rounded-[1.5rem] border border-indigo-200 bg-white/95 px-4 py-3 shadow-[0_18px_50px_rgba(79,70,229,0.12)] backdrop-blur-xl"
		>
			<textarea
				value={value}
				onChange={(event) => onChange(event.target.value)}
				onKeyDown={handleKeyDown}
				placeholder="Ask anything about your education journey..."
				rows={1}
				className="max-h-32 min-h-12 w-full resize-none bg-transparent text-sm font-semibold leading-6 text-slate-800 outline-none placeholder:text-slate-400 md:text-base"
			/>
			<div className="mt-2 flex items-center justify-between gap-3">
				<div className="flex items-center gap-2">
					<button
						type="button"
						aria-label="Attach file"
						className="flex h-9 w-9 items-center justify-center rounded-full text-slate-500 transition hover:bg-slate-100 hover:text-indigo-600"
					>
						<FaPaperclip />
					</button>
					<button
						type="button"
						aria-label="Attach image"
						className="flex h-9 w-9 items-center justify-center rounded-full text-slate-500 transition hover:bg-slate-100 hover:text-indigo-600"
					>
						<FaImage />
					</button>
				</div>
				<button
					type="submit"
					aria-label="Send message"
					disabled={!canSend}
					className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-0.5 hover:shadow-indigo-300 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
				>
					<FaPaperPlane />
				</button>
			</div>
		</form>
	);
};

export default MessageComposer;
